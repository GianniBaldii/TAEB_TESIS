from decimal import Decimal

from django.db import transaction

from apps.alumnos.models import Alumno, Examen, ExamenDetalle, ExamenTemplateItem

from . import alumno_service, examen_template_service
from .excepciones import AlumnosError


ESTADOS_FINALES = {
    Examen.Estado.APROBADO,
    Examen.Estado.DESAPROBADO,
    Examen.Estado.AUSENTE,
    Examen.Estado.ANULADO,
}

CONCEPTOS_GUP_VALIDOS = (
    "NAN-", "NAN", "NAN+", "AN-", "AN", "AN+", "SN-", "SN", "SN+",
)


def validar_puede_crear_examen_actual(alumno, cinturon_destino):
    if Examen.objects.filter(
        alumno=alumno,
        es_historico=False,
        estado=Examen.Estado.PENDIENTE,
    ).exists():
        raise AlumnosError(
            "El alumno ya tiene un examen pendiente. Primero debe resolverlo, "
            "desaprobarlo o anularlo."
        )
    if Examen.objects.filter(
        alumno=alumno,
        cinturon_destino=cinturon_destino,
        estado=Examen.Estado.APROBADO,
    ).exists():
        raise AlumnosError("El alumno ya aprobó un examen para este cinturón.")


def validar_examen_historico_duplicado(alumno, cinturon_destino, fecha_examen):
    if Examen.objects.filter(
        alumno=alumno,
        cinturon_destino=cinturon_destino,
        fecha_examen=fecha_examen,
        es_historico=True,
    ).exists():
        raise AlumnosError(
            "Ya existe un examen histórico para este alumno, cinturón y fecha."
        )


def validar_cinturon_destino_rendible(cinturon_destino):
    cinturon_inicial = alumno_service.obtener_cinturon_inicial()
    if cinturon_inicial and cinturon_destino.pk == cinturon_inicial.pk:
        raise AlumnosError(
            "El cinturón inicial no puede ser destino de un examen; se asigna al "
            "comenzar Taekwondo."
        )


def _validar_concepto_gup(examen, concepto):
    if (
        examen.cinturon_destino.tipo_rango == "GUP"
        and concepto
        and concepto not in CONCEPTOS_GUP_VALIDOS
    ):
        raise AlumnosError(
            "El concepto indicado no es válido para un examen GUP."
        )


def examen_tiene_estado_final(examen):
    return examen.estado in ESTADOS_FINALES


def validar_examen_pendiente(examen, accion):
    if examen_tiene_estado_final(examen):
        raise AlumnosError(
            f"No se puede {accion} un examen con estado final "
            f"{examen.get_estado_display()}."
        )
    return True


@transaction.atomic
def crear_examen_para_alumno(
    alumno,
    fecha_examen,
    lugar=None,
    cinturon_destino=None,
    es_historico=False,
):
    # Bloqueamos al alumno para que dos solicitudes simultáneas no creen pendientes.
    alumno = Alumno.objects.select_for_update().select_related("cinturon_actual").get(
        pk=alumno.pk
    )
    if es_historico:
        if not cinturon_destino:
            raise AlumnosError("Seleccione un cinturón destino para el examen histórico.")
        validar_cinturon_destino_rendible(cinturon_destino)
        cinturon_origen = alumno_service.obtener_cinturon_anterior(cinturon_destino)
        if not cinturon_origen:
            raise AlumnosError(
                "No se puede determinar el cinturón origen para el destino seleccionado."
            )
        validar_examen_historico_duplicado(alumno, cinturon_destino, fecha_examen)
    else:
        cinturon_origen = alumno.cinturon_actual
        if not cinturon_origen:
            raise AlumnosError("El alumno debe tener un cinturón actual para crear un examen.")
        cinturon_destino = alumno_service.obtener_siguiente_cinturon(cinturon_origen)
        if not cinturon_destino:
            raise AlumnosError("No existe un siguiente cinturón activo para el alumno.")
        validar_cinturon_destino_rendible(cinturon_destino)
        validar_puede_crear_examen_actual(alumno, cinturon_destino)
    if not cinturon_destino:
        raise AlumnosError("No existe un siguiente cinturon activo para el alumno.")
    if cinturon_destino.orden <= cinturon_origen.orden:
        raise AlumnosError("El cinturon destino debe ser posterior al cinturon origen.")

    template = examen_template_service.obtener_template_activo_para_cinturon(
        cinturon_destino
    )
    examen = Examen.objects.create(
        alumno=alumno,
        examen_template=template,
        cinturon_origen=cinturon_origen,
        cinturon_destino=cinturon_destino,
        fecha_examen=fecha_examen,
        lugar=lugar,
        es_historico=es_historico,
        estado=Examen.Estado.PENDIENTE,
    )
    generar_detalles_desde_template(examen)
    return examen


def generar_detalles_desde_template(examen):
    items = ExamenTemplateItem.objects.filter(
        seccion__examen_template=examen.examen_template,
        seccion__activo=True,
        activo=True,
    ).select_related("seccion")
    existentes = set(
        examen.detalles.filter(template_item__in=items).values_list(
            "template_item_id", flat=True
        )
    )
    nuevos = [
        ExamenDetalle(examen=examen, template_item=item)
        for item in items
        if item.pk not in existentes
    ]
    if nuevos:
        ExamenDetalle.objects.bulk_create(nuevos)
    return examen.detalles.select_related("template_item", "template_item__seccion")


def actualizar_evaluaciones_examen(examen, evaluaciones_data):
    validar_examen_pendiente(examen, "editar")
    detalles_data = evaluaciones_data.get("detalles", {})
    for detalle in examen.detalles.select_related("template_item"):
        data = detalles_data.get(detalle.pk) or detalles_data.get(str(detalle.pk))
        if data is None:
            continue
        tipo = detalle.template_item.tipo_evaluacion
        if tipo == ExamenTemplateItem.TipoEvaluacion.NUMERICA:
            detalle.nota_numerica = data.get("nota_numerica") or None
        elif tipo == ExamenTemplateItem.TipoEvaluacion.CONCEPTO:
            concepto = data.get("concepto") or None
            _validar_concepto_gup(examen, concepto)
            detalle.concepto = concepto
        elif tipo == ExamenTemplateItem.TipoEvaluacion.TEXTO:
            detalle.valor_texto = data.get("valor_texto") or None
        elif tipo == ExamenTemplateItem.TipoEvaluacion.CHECK:
            aprobado = data.get("aprobado")
            if aprobado == "true":
                detalle.aprobado = True
            elif aprobado == "false":
                detalle.aprobado = False
            else:
                detalle.aprobado = None
        detalle.observaciones = data.get("observaciones") or None
        detalle.save()

    _validar_concepto_gup(examen, evaluaciones_data.get("resultado_final"))
    for campo in ("nota_final", "resultado_final", "observaciones"):
        if campo in evaluaciones_data:
            setattr(examen, campo, evaluaciones_data.get(campo) or None)
    examen.save(update_fields=["nota_final", "resultado_final", "observaciones", "fecha_modificacion"])
    return examen


def validar_items_obligatorios_evaluados(examen):
    faltantes = []
    detalles = examen.detalles.select_related("template_item", "template_item__seccion")
    for detalle in detalles:
        item = detalle.template_item
        if not item.activo or not item.obligatorio or not item.seccion.activo:
            continue
        if item.tipo_evaluacion == ExamenTemplateItem.TipoEvaluacion.NUMERICA:
            falta = detalle.nota_numerica is None
        elif item.tipo_evaluacion == ExamenTemplateItem.TipoEvaluacion.CONCEPTO:
            falta = not detalle.concepto
        elif item.tipo_evaluacion == ExamenTemplateItem.TipoEvaluacion.TEXTO:
            falta = not detalle.valor_texto
        elif item.tipo_evaluacion == ExamenTemplateItem.TipoEvaluacion.CHECK:
            falta = detalle.aprobado is None
        else:
            falta = False
        if falta:
            faltantes.append(f"{item.seccion.nombre} / {item.nombre}")

    if faltantes:
        raise AlumnosError(
            "Faltan evaluar items obligatorios: " + ", ".join(faltantes)
        )
    return True


@transaction.atomic
def aprobar_examen(examen):
    validar_examen_pendiente(examen, "aprobar")
    if not examen.es_historico:
        validar_items_obligatorios_evaluados(examen)
    examen.estado = Examen.Estado.APROBADO
    examen.save(update_fields=["estado", "fecha_modificacion"])
    alumno_service.registrar_cambio_cinturon_por_examen(examen)
    return examen


def desaprobar_examen(examen):
    validar_examen_pendiente(examen, "desaprobar")
    examen.estado = Examen.Estado.DESAPROBADO
    examen.save(update_fields=["estado", "fecha_modificacion"])
    return examen


def anular_examen(examen):
    validar_examen_pendiente(examen, "anular")
    examen.estado = Examen.Estado.ANULADO
    examen.save(update_fields=["estado", "fecha_modificacion"])
    return examen


def calcular_nota_final(examen):
    total = Decimal("0")
    ponderacion_total = Decimal("0")
    for detalle in examen.detalles.select_related("template_item"):
        item = detalle.template_item
        if (
            item.tipo_evaluacion != ExamenTemplateItem.TipoEvaluacion.NUMERICA
            or detalle.nota_numerica is None
        ):
            continue
        total += detalle.nota_numerica * item.ponderacion
        ponderacion_total += item.ponderacion
    if ponderacion_total == 0:
        return None
    return total / ponderacion_total
