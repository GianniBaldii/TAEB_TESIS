from datetime import timedelta

from django.core.exceptions import ValidationError

from ..models import ClaseHorario
from .excepciones import ClasesError


HORARIO_CAMPOS_EDITABLES = {
    "dia_semana",
    "hora_inicio",
    "hora_fin",
    "fecha_desde",
    "fecha_hasta",
    "activo",
}


def _normalizar_data(data):
    return {campo: valor for campo, valor in data.items() if campo in HORARIO_CAMPOS_EDITABLES}


def _validar_horario(horario):
    try:
        horario.full_clean()
    except ValidationError as exc:
        raise ClasesError(exc) from exc


def crear_horario_clase(clase, data):
    if not clase.activo:
        raise ClasesError("No se pueden agregar horarios a una clase inactiva.")
    horario = ClaseHorario(clase=clase, **_normalizar_data(data))
    _validar_horario(horario)
    horario.save()
    return horario


def actualizar_horario_clase(horario, data):
    for campo, valor in _normalizar_data(data).items():
        setattr(horario, campo, valor)
    _validar_horario(horario)
    horario.save()
    return horario


def desactivar_horario_clase(horario):
    horario.activo = False
    horario.save(update_fields=["activo", "fecha_modificacion"])
    return horario


def obtener_ocurrencias_calendario(escuela, fecha_desde, fecha_hasta):
    horarios = (
        ClaseHorario.objects.select_related(
            "clase",
            "clase__escuela",
            "clase__docente_responsable",
            "clase__docente_responsable__docente__usuario",
        )
        .filter(clase__escuela=escuela, clase__activo=True, activo=True)
        .exclude(fecha_hasta__lt=fecha_desde)
        .exclude(fecha_desde__gt=fecha_hasta)
    )
    ocurrencias = []
    for horario in horarios:
        cursor = fecha_desde
        while cursor <= fecha_hasta:
            if cursor.weekday() == horario.dia_semana:
                desde_ok = not horario.fecha_desde or cursor >= horario.fecha_desde
                hasta_ok = not horario.fecha_hasta or cursor <= horario.fecha_hasta
                if desde_ok and hasta_ok:
                    ocurrencias.append(
                        {
                            "tipo": "ocurrencia",
                            "clase": horario.clase,
                            "horario": horario,
                            "fecha": cursor,
                            "hora_inicio": horario.hora_inicio,
                            "hora_fin": horario.hora_fin,
                            "estado": "PROGRAMADA",
                        }
                    )
            cursor += timedelta(days=1)
    return sorted(ocurrencias, key=lambda item: (item["fecha"], item["hora_inicio"]))

