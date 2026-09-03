from decimal import Decimal

from django.db.models import Case, DecimalField, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.alumnos.models import AlumnoEscuela
from apps.clases.models import Clase, ClaseAlumno
from ..models import ObligacionPago, Pago


def alumnos_activos(escuela):
    return AlumnoEscuela.objects.select_related("alumno", "alumno__cinturon_actual").filter(escuela=escuela, activo=True, alumno__activo=True).order_by("alumno__apellido", "alumno__nombre")


def clases_activas(escuela):
    return Clase.objects.filter(escuela=escuela, activo=True).order_by("nombre")


def alumnos_de_clase(clase):
    ids = ClaseAlumno.objects.filter(clase=clase, activo=True, alumno_escuela__activo=True, alumno_escuela__alumno__activo=True).values_list("alumno_escuela_id", flat=True)
    return AlumnoEscuela.objects.select_related("alumno").filter(pk__in=ids).distinct()


def obligaciones_con_saldo(queryset=None):
    if queryset is None:
        queryset = ObligacionPago.objects.all()
    cero = Value(Decimal("0.00"), output_field=DecimalField(max_digits=12, decimal_places=2))
    return queryset.select_related("escuela", "alumno_escuela__alumno", "concepto_financiero").prefetch_related("alumno_escuela__clases_inscriptas__clase").annotate(
        monto_pagado=Coalesce(Sum("aplicaciones_pago__monto_aplicado", filter=Q(aplicaciones_pago__pago__estado=Pago.Estado.CONFIRMADO)), cero),
    ).annotate(saldo=F("monto_original") - F("monto_pagado"))


def obligaciones_de_periodo(*, escuela, anio, mes, clase=None):
    qs = obligaciones_con_saldo(ObligacionPago.objects.filter(escuela=escuela, periodo_anio=anio, periodo_mes=mes, estado_operativo=ObligacionPago.EstadoOperativo.ACTIVA))
    if clase:
        qs = qs.filter(alumno_escuela__clases_inscriptas__clase=clase, alumno_escuela__clases_inscriptas__activo=True).distinct()
    return qs


def obligaciones_de_alumno(inscripcion):
    return obligaciones_con_saldo(ObligacionPago.objects.filter(alumno_escuela=inscripcion)).prefetch_related("aplicaciones_pago__pago")


def estado_obligacion(obligacion, hoy=None):
    hoy = hoy or timezone.localdate()
    if obligacion.estado_operativo == ObligacionPago.EstadoOperativo.ANULADA:
        return {"pago": "ANULADA", "temporal": ""}
    saldo = obligacion.saldo
    if saldo == 0:
        pago = "PAGADA"
    elif saldo < obligacion.monto_original:
        pago = "PARCIAL"
    else:
        pago = "PENDIENTE"
    temporal = "ATRASADA" if saldo > 0 and hoy >= obligacion.fecha_atraso else ("VENCIDA" if saldo > 0 and hoy > obligacion.fecha_vencimiento else "VIGENTE")
    return {"pago": pago, "temporal": temporal}


def resumen_periodo(obligaciones):
    items = list(obligaciones)
    resumen = {"total": len(items), "pagadas": 0, "parciales": 0, "pendientes": 0, "atrasadas": 0, "facturado": Decimal("0"), "cobrado": Decimal("0"), "saldo": Decimal("0")}
    for item in items:
        estado = estado_obligacion(item)
        resumen["facturado"] += item.monto_original
        resumen["cobrado"] += item.monto_pagado
        resumen["saldo"] += item.saldo
        if estado["pago"] == "PAGADA": resumen["pagadas"] += 1
        elif estado["pago"] == "PARCIAL": resumen["parciales"] += 1
        else: resumen["pendientes"] += 1
        if estado["temporal"] == "ATRASADA": resumen["atrasadas"] += 1
        item.estado_financiero = estado
    return items, resumen
