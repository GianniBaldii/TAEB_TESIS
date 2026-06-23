from django.db import transaction
from django.db.models import Prefetch

from apps.alumnos.models import (
    ExamenTemplate,
    ExamenTemplateItem,
    ExamenTemplateSeccion,
)

from .excepciones import AlumnosError


TEMPLATE_CAMPOS = {
    "cinturon",
    "nombre",
    "descripcion",
    "nota_minima_aprobacion",
    "vigente_desde",
    "vigente_hasta",
}
SECCION_CAMPOS = {"nombre", "descripcion", "orden", "obligatorio", "activo"}
ITEM_CAMPOS = {
    "nombre",
    "descripcion",
    "tipo_evaluacion",
    "orden",
    "puntaje_maximo",
    "ponderacion",
    "obligatorio",
    "activo",
}


def _filtrar(data, campos):
    return {campo: valor for campo, valor in data.items() if campo in campos}


def obtener_template_activo_para_cinturon(cinturon):
    template = (
        ExamenTemplate.objects.filter(cinturon=cinturon, activo=True)
        .order_by("-version", "-fecha_creacion")
        .first()
    )
    if not template:
        raise AlumnosError("No existe un template activo para el cinturon destino.")
    return template


def template_tiene_examenes_asociados(template):
    return template.examenes.exists()


def validar_template_editable(template):
    if template_tiene_examenes_asociados(template):
        raise AlumnosError(
            "Este template ya fue utilizado en exámenes y no puede modificarse. "
            "Creá una nueva versión para actualizar los criterios."
        )
    return True


def crear_template(data):
    template = ExamenTemplate.objects.create(**_filtrar(data, TEMPLATE_CAMPOS))
    return template


def actualizar_template(template, data):
    validar_template_editable(template)
    datos = _filtrar(data, TEMPLATE_CAMPOS)
    for campo, valor in datos.items():
        setattr(template, campo, valor)
    template.save(update_fields=[*list(datos.keys()), "fecha_modificacion"])
    return template


@transaction.atomic
def duplicar_template(template):
    template = ExamenTemplate.objects.select_for_update().get(pk=template.pk)
    nuevo_template = ExamenTemplate.objects.create(
        cinturon=template.cinturon,
        nombre=template.nombre,
        descripcion=template.descripcion,
        nota_minima_aprobacion=template.nota_minima_aprobacion,
        version=template.version + 1,
        template_origen=template,
        vigente_desde=template.vigente_desde,
        vigente_hasta=template.vigente_hasta,
        activo=False,
    )
    for seccion in template.secciones.all().order_by("orden", "pk"):
        nueva_seccion = ExamenTemplateSeccion.objects.create(
            examen_template=nuevo_template,
            nombre=seccion.nombre,
            descripcion=seccion.descripcion,
            orden=seccion.orden,
            obligatorio=seccion.obligatorio,
            activo=seccion.activo,
        )
        ExamenTemplateItem.objects.bulk_create(
            [
                ExamenTemplateItem(
                    seccion=nueva_seccion,
                    nombre=item.nombre,
                    descripcion=item.descripcion,
                    tipo_evaluacion=item.tipo_evaluacion,
                    orden=item.orden,
                    puntaje_maximo=item.puntaje_maximo,
                    ponderacion=item.ponderacion,
                    obligatorio=item.obligatorio,
                    activo=item.activo,
                )
                for item in seccion.items.all().order_by("orden", "pk")
            ]
        )
    return nuevo_template


@transaction.atomic
def activar_template(template):
    ExamenTemplate.objects.filter(cinturon=template.cinturon, activo=True).exclude(
        pk=template.pk
    ).update(activo=False)
    template.activo = True
    template.save(update_fields=["activo", "fecha_modificacion"])
    return template


def desactivar_template(template):
    template.activo = False
    template.save(update_fields=["activo", "fecha_modificacion"])
    return template


@transaction.atomic
def eliminar_template(template):
    validar_template_editable(template)
    template.delete()


def crear_seccion(template, data):
    validar_template_editable(template)
    return ExamenTemplateSeccion.objects.create(
        examen_template=template, **_filtrar(data, SECCION_CAMPOS)
    )


def actualizar_seccion(seccion, data):
    validar_template_editable(seccion.examen_template)
    datos = _filtrar(data, SECCION_CAMPOS)
    for campo, valor in datos.items():
        setattr(seccion, campo, valor)
    seccion.save(update_fields=list(datos.keys()))
    return seccion


def desactivar_seccion(seccion):
    validar_template_editable(seccion.examen_template)
    seccion.activo = False
    seccion.save(update_fields=["activo"])
    return seccion


def crear_item(seccion, data):
    validar_template_editable(seccion.examen_template)
    return ExamenTemplateItem.objects.create(seccion=seccion, **_filtrar(data, ITEM_CAMPOS))


def actualizar_item(item, data):
    validar_template_editable(item.seccion.examen_template)
    datos = _filtrar(data, ITEM_CAMPOS)
    for campo, valor in datos.items():
        setattr(item, campo, valor)
    item.save(update_fields=list(datos.keys()))
    return item


def desactivar_item(item):
    validar_template_editable(item.seccion.examen_template)
    item.activo = False
    item.save(update_fields=["activo"])
    return item


def obtener_estructura_template(template):
    return (
        ExamenTemplate.objects.filter(pk=template.pk)
        .prefetch_related(
            Prefetch(
                "secciones",
                queryset=ExamenTemplateSeccion.objects.filter(activo=True)
                .order_by("orden")
                .prefetch_related(
                    Prefetch(
                        "items",
                        queryset=ExamenTemplateItem.objects.filter(activo=True).order_by(
                            "orden"
                        ),
                    )
                ),
            )
        )
        .select_related("cinturon")
        .get()
        .secciones.all()
    )
