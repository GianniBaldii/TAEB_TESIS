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
    "version",
    "activo",
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


def crear_template(data):
    template = ExamenTemplate.objects.create(**_filtrar(data, TEMPLATE_CAMPOS))
    if template.activo:
        activar_template(template)
    return template


def actualizar_template(template, data):
    # TODO: cuando haya versionado avanzado, evitar cambios estructurales sensibles.
    datos = _filtrar(data, TEMPLATE_CAMPOS)
    for campo, valor in datos.items():
        setattr(template, campo, valor)
    template.save(update_fields=[*list(datos.keys()), "fecha_modificacion"])
    if template.activo:
        activar_template(template)
    return template


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


def crear_seccion(template, data):
    return ExamenTemplateSeccion.objects.create(
        examen_template=template, **_filtrar(data, SECCION_CAMPOS)
    )


def actualizar_seccion(seccion, data):
    datos = _filtrar(data, SECCION_CAMPOS)
    for campo, valor in datos.items():
        setattr(seccion, campo, valor)
    seccion.save(update_fields=list(datos.keys()))
    return seccion


def desactivar_seccion(seccion):
    seccion.activo = False
    seccion.save(update_fields=["activo"])
    return seccion


def crear_item(seccion, data):
    return ExamenTemplateItem.objects.create(seccion=seccion, **_filtrar(data, ITEM_CAMPOS))


def actualizar_item(item, data):
    datos = _filtrar(data, ITEM_CAMPOS)
    for campo, valor in datos.items():
        setattr(item, campo, valor)
    item.save(update_fields=list(datos.keys()))
    return item


def desactivar_item(item):
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
