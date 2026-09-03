from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.alumnos.models import AlumnoEscuela
from apps.clases.models import AsistenciaClase, Clase, ClaseSesion
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario
from apps.escuelas.services.excepciones import EscuelaActivaNoEncontradaError
from apps.finanzas.models import ObligacionPago, Pago
from apps.finanzas.selectors.finanzas_selectors import obligaciones_con_saldo


def _escuela_visible(usuario):
    if usuario.is_superuser:
        return None
    try:
        return obtener_escuela_activa_usuario(usuario)
    except EscuelaActivaNoEncontradaError:
        return False


def resumen_dashboard(usuario):
    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)
    escuela = _escuela_visible(usuario)
    inscripciones = AlumnoEscuela.objects.filter(activo=True, alumno__activo=True)
    clases = Clase.objects.filter(activo=True)
    sesiones = ClaseSesion.objects.select_related("clase", "clase__escuela")
    asistencias = AsistenciaClase.objects.filter(sesion__fecha__gte=inicio_mes)
    obligaciones = ObligacionPago.objects.filter(
        estado_operativo=ObligacionPago.EstadoOperativo.ACTIVA,
        periodo_anio=hoy.year,
        periodo_mes=hoy.month,
    )
    pagos = Pago.objects.filter(
        estado=Pago.Estado.CONFIRMADO,
        fecha_pago__range=(inicio_mes, hoy),
    )

    if escuela is False:
        inscripciones = inscripciones.none()
        clases = clases.none()
        sesiones = sesiones.none()
        asistencias = asistencias.none()
        obligaciones = obligaciones.none()
        pagos = pagos.none()
    elif escuela is not None:
        inscripciones = inscripciones.filter(escuela=escuela)
        clases = clases.filter(escuela=escuela)
        sesiones = sesiones.filter(clase__escuela=escuela)
        asistencias = asistencias.filter(sesion__clase__escuela=escuela)
        obligaciones = obligaciones.filter(escuela=escuela)
        pagos = pagos.filter(escuela=escuela)

    cerradas = asistencias.exclude(estado=AsistenciaClase.Estado.PENDIENTE)
    total_asistencias = cerradas.count()
    positivas = cerradas.filter(
        estado__in=[AsistenciaClase.Estado.PRESENTE, AsistenciaClase.Estado.TARDE]
    ).count()
    financiero = {"facturado": Decimal("0.00"), "saldo": Decimal("0.00"), "pendientes": 0, "vencidas": 0}
    for obligacion in obligaciones_con_saldo(obligaciones):
        financiero["facturado"] += obligacion.monto_original
        financiero["saldo"] += obligacion.saldo
        if obligacion.saldo > 0:
            financiero["pendientes"] += 1
            if hoy > obligacion.fecha_vencimiento:
                financiero["vencidas"] += 1
    financiero["cobrado"] = pagos.aggregate(total=Sum("monto_total"))["total"] or Decimal("0.00")

    proximas_sesiones = sesiones.filter(fecha__gte=hoy).exclude(
        estado=ClaseSesion.Estado.CANCELADA
    ).order_by("fecha", "hora_inicio")[:5]
    return {
        "hoy": hoy,
        "escuela_dashboard": escuela if escuela is not False else None,
        "sin_escuela": escuela is False,
        "alumnos_activos": inscripciones.values("alumno_id").distinct().count(),
        "clases_activas": clases.count(),
        "clases_hoy": sesiones.filter(fecha=hoy).exclude(estado=ClaseSesion.Estado.CANCELADA).count(),
        "asistencias_pendientes": asistencias.filter(estado=AsistenciaClase.Estado.PENDIENTE, sesion__fecha__lte=hoy).count(),
        "porcentaje_asistencia": round(positivas * 100 / total_asistencias) if total_asistencias else 0,
        "total_asistencias_mes": total_asistencias,
        "resumen_financiero": financiero,
        "proximas_sesiones": proximas_sesiones,
        "sesiones_sin_cerrar": sesiones.filter(
            fecha__lte=hoy,
            estado__in=[ClaseSesion.Estado.PROGRAMADA, ClaseSesion.Estado.EN_CURSO],
        ).count(),
    }
