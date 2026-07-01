from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from ..models import ClaseSesion
from .excepciones import ClasesError


def _validar_sesion(sesion):
    try:
        sesion.full_clean()
    except ValidationError as exc:
        raise ClasesError(exc) from exc


@transaction.atomic
def crear_o_obtener_sesion(clase, horario, fecha, docente_a_cargo=None):
    if not clase.activo:
        raise ClasesError("No se pueden crear sesiones para una clase inactiva.")
    if horario.clase_id != clase.id:
        raise ClasesError("El horario no pertenece a la clase indicada.")
    defaults = {
        "horario": horario,
        "hora_fin": horario.hora_fin,
        "docente_a_cargo": docente_a_cargo or clase.docente_responsable,
    }
    try:
        sesion, creada = ClaseSesion.objects.get_or_create(
            clase=clase,
            fecha=fecha,
            hora_inicio=horario.hora_inicio,
            defaults=defaults,
        )
    except IntegrityError:
        sesion = ClaseSesion.objects.get(
            clase=clase,
            fecha=fecha,
            hora_inicio=horario.hora_inicio,
        )
        creada = False
    if creada:
        _validar_sesion(sesion)
    return sesion


def crear_clase_extra(clase, fecha, hora_inicio, hora_fin, docente_a_cargo=None, observaciones=None):
    if not clase.activo:
        raise ClasesError("No se pueden crear sesiones para una clase inactiva.")
    sesion = ClaseSesion(
        clase=clase,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        docente_a_cargo=docente_a_cargo or clase.docente_responsable,
        es_clase_extra=True,
        observaciones=observaciones,
    )
    _validar_sesion(sesion)
    sesion.save()
    return sesion


def cancelar_sesion(sesion, motivo):
    if sesion.estado == ClaseSesion.Estado.FINALIZADA:
        raise ClasesError("No se puede cancelar una sesion finalizada.")
    if not motivo:
        raise ClasesError("Debe indicar un motivo de cancelacion.")
    sesion.estado = ClaseSesion.Estado.CANCELADA
    sesion.motivo_cancelacion = motivo
    sesion.save(update_fields=["estado", "motivo_cancelacion", "fecha_modificacion"])
    return sesion


def iniciar_sesion(sesion):
    if sesion.estado == ClaseSesion.Estado.CANCELADA:
        raise ClasesError("No se puede iniciar una sesion cancelada.")
    sesion.estado = ClaseSesion.Estado.EN_CURSO
    sesion.save(update_fields=["estado", "fecha_modificacion"])
    return sesion


def finalizar_sesion(sesion):
    if sesion.estado == ClaseSesion.Estado.CANCELADA:
        raise ClasesError("No se puede finalizar una sesion cancelada.")
    sesion.estado = ClaseSesion.Estado.FINALIZADA
    sesion.save(update_fields=["estado", "fecha_modificacion"])
    return sesion


def reabrir_sesion(sesion):
    if sesion.estado == ClaseSesion.Estado.CANCELADA:
        raise ClasesError("No se puede reabrir una sesion cancelada.")
    sesion.estado = ClaseSesion.Estado.EN_CURSO
    sesion.save(update_fields=["estado", "fecha_modificacion"])
    return sesion


def obtener_sesiones_calendario(escuela, fecha_desde, fecha_hasta):
    return (
        ClaseSesion.objects.select_related(
            "clase",
            "clase__escuela",
            "docente_a_cargo",
            "docente_a_cargo__docente__usuario",
        )
        .filter(clase__escuela=escuela, fecha__gte=fecha_desde, fecha__lte=fecha_hasta)
        .order_by("fecha", "hora_inicio")
    )

