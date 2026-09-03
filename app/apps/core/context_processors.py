from django.utils import timezone

from apps.clases.models import AsistenciaClase, ClaseSesion
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario
from apps.escuelas.services.excepciones import EscuelaActivaNoEncontradaError
from apps.finanzas.models import ObligacionPago
from apps.finanzas.selectors.finanzas_selectors import obligaciones_con_saldo


def barra_superior(request):
    if not request.user.is_authenticated:
        return {}

    hoy = timezone.localdate()
    escuela = None
    sin_escuela = False
    if not request.user.is_superuser:
        try:
            escuela = obtener_escuela_activa_usuario(request.user)
        except EscuelaActivaNoEncontradaError:
            sin_escuela = True

    sesiones = ClaseSesion.objects.all()
    asistencias = AsistenciaClase.objects.filter(
        estado=AsistenciaClase.Estado.PENDIENTE,
        sesion__fecha__lte=hoy,
    )
    obligaciones = ObligacionPago.objects.filter(
        estado_operativo=ObligacionPago.EstadoOperativo.ACTIVA,
        fecha_vencimiento__lt=hoy,
    )

    if sin_escuela:
        sesiones = sesiones.none()
        asistencias = asistencias.none()
        obligaciones = obligaciones.none()
    elif escuela is not None:
        sesiones = sesiones.filter(clase__escuela=escuela)
        asistencias = asistencias.filter(sesion__clase__escuela=escuela)
        obligaciones = obligaciones.filter(escuela=escuela)

    sesiones_pendientes = sesiones.filter(
        fecha__lte=hoy,
        estado__in=[ClaseSesion.Estado.PROGRAMADA, ClaseSesion.Estado.EN_CURSO],
    ).count()
    asistencias_pendientes = asistencias.count()
    cuotas_vencidas = obligaciones_con_saldo(obligaciones).filter(saldo__gt=0).count()

    return {
        "barra_escuela": escuela,
        "barra_sin_escuela": sin_escuela,
        "barra_alertas": {
            "sesiones": sesiones_pendientes,
            "asistencias": asistencias_pendientes,
            "cuotas": cuotas_vencidas,
            "total": sesiones_pendientes + asistencias_pendientes + cuotas_vencidas,
        },
    }
