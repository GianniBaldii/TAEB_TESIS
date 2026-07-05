from django.db import transaction
from django.db.models import Count, Q

from ..models import AsistenciaClase, ClaseSesion
from .clase_alumno_service import obtener_alumnos_activos_de_clase
from .excepciones import ClasesError


def _validar_sesion_editable(sesion):
    if sesion.estado == ClaseSesion.Estado.CANCELADA:
        raise ClasesError("No se puede tomar asistencia en una sesion cancelada.")
    if sesion.estado == ClaseSesion.Estado.FINALIZADA:
        raise ClasesError("La sesion esta finalizada. Debe reabrirla para editar asistencia.")


@transaction.atomic
def inicializar_asistencias_sesion(sesion, usuario):
    _validar_sesion_editable(sesion)
    for clase_alumno in obtener_alumnos_activos_de_clase(sesion.clase, sesion.fecha):
        AsistenciaClase.objects.get_or_create(
            sesion=sesion,
            clase_alumno=clase_alumno,
            defaults={"estado": AsistenciaClase.Estado.PENDIENTE, "registrado_por": usuario},
        )
    return sesion.asistencias.select_related(
        "clase_alumno__alumno_escuela__alumno",
        "clase_alumno__alumno_escuela__alumno__cinturon_actual",
    )


def actualizar_asistencia(asistencia, estado, observaciones, usuario):
    _validar_sesion_editable(asistencia.sesion)
    asistencia.estado = estado
    asistencia.observaciones = observaciones
    asistencia.registrado_por = usuario
    asistencia.save(
        update_fields=["estado", "observaciones", "registrado_por", "fecha_modificacion"]
    )
    return asistencia


def marcar_todos_presentes(sesion, usuario):
    _validar_sesion_editable(sesion)
    inicializar_asistencias_sesion(sesion, usuario)
    sesion.asistencias.update(
        estado=AsistenciaClase.Estado.PRESENTE,
        registrado_por=usuario,
    )


def marcar_todos_ausentes(sesion, usuario):
    _validar_sesion_editable(sesion)
    inicializar_asistencias_sesion(sesion, usuario)
    sesion.asistencias.update(
        estado=AsistenciaClase.Estado.AUSENTE,
        registrado_por=usuario,
    )


@transaction.atomic
def guardar_asistencias_sesion(sesion, datos_asistencias, usuario):
    _validar_sesion_editable(sesion)
    asistencias = sesion.asistencias.select_related("sesion")
    for asistencia in asistencias:
        datos = datos_asistencias.get(str(asistencia.pk)) or datos_asistencias.get(asistencia.pk)
        if not datos:
            continue
        actualizar_asistencia(
            asistencia,
            datos.get("estado", asistencia.estado),
            datos.get("observaciones", asistencia.observaciones),
            usuario,
        )
    return sesion


@transaction.atomic
def cerrar_asistencia_sesion(sesion, usuario):
    _validar_sesion_editable(sesion)
    inicializar_asistencias_sesion(sesion, usuario)
    sesion.asistencias.filter(estado=AsistenciaClase.Estado.PENDIENTE).update(
        estado=AsistenciaClase.Estado.AUSENTE,
        registrado_por=usuario,
    )
    sesion.estado = ClaseSesion.Estado.FINALIZADA
    sesion.save(update_fields=["estado", "fecha_modificacion"])
    return sesion


def reabrir_asistencia_sesion(sesion, usuario):
    if sesion.estado == ClaseSesion.Estado.CANCELADA:
        raise ClasesError("No se puede reabrir asistencia de una sesion cancelada.")
    sesion.estado = ClaseSesion.Estado.EN_CURSO
    sesion.save(update_fields=["estado", "fecha_modificacion"])
    return sesion


def obtener_resumen_asistencia_sesion(sesion):
    conteos = sesion.asistencias.aggregate(
        pendientes=Count("id", filter=Q(estado=AsistenciaClase.Estado.PENDIENTE)),
        presentes=Count("id", filter=Q(estado=AsistenciaClase.Estado.PRESENTE)),
        ausentes=Count("id", filter=Q(estado=AsistenciaClase.Estado.AUSENTE)),
        justificadas=Count("id", filter=Q(estado=AsistenciaClase.Estado.JUSTIFICADA)),
        tarde=Count("id", filter=Q(estado=AsistenciaClase.Estado.TARDE)),
    )
    return {clave: valor or 0 for clave, valor in conteos.items()}
