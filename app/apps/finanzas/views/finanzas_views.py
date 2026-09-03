from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.alumnos.models import AlumnoEscuela
from ..forms import ConfiguracionCuotaForm
from ..models import ConceptoFinanciero, ConfiguracionCuota
from ..selectors.finanzas_selectors import estado_obligacion, obligaciones_de_alumno
from ..services import configuracion_financiera_service
from ._helpers import escuela_operativa, obligacion_accesible


@login_required
def configuracion(request):
    escuela = escuela_operativa(request)
    configuracion_actual = ConfiguracionCuota.objects.filter(escuela=escuela).first()
    conceptos = configuracion_financiera_service.asegurar_conceptos(escuela)
    form = ConfiguracionCuotaForm(request.POST or None, instance=configuracion_actual)
    if request.method == "POST" and form.is_valid():
        configuracion_financiera_service.guardar_configuracion_cuota(escuela=escuela, datos=form.cleaned_data, usuario=request.user)
        messages.success(request, "Configuración financiera guardada.")
        return redirect("finanzas:configuracion")
    return render(request, "finanzas/configuracion.html", {"form": form, "conceptos": conceptos})


@login_required
def toggle_concepto(request, pk):
    escuela = escuela_operativa(request)
    concepto = get_object_or_404(ConceptoFinanciero, pk=pk, escuela=escuela)
    if request.method == "POST":
        configuracion_financiera_service.cambiar_estado_concepto(concepto=concepto, activo=not concepto.activo, usuario=request.user)
    return redirect("finanzas:configuracion")


@login_required
def obligacion_detail(request, pk):
    obligacion = obligacion_accesible(request, pk)
    obligacion.estado_financiero = estado_obligacion(obligacion)
    aplicaciones = obligacion.aplicaciones_pago.select_related("pago").filter(pago__estado="CONFIRMADO")
    return render(request, "finanzas/obligacion_detail.html", {"obligacion": obligacion, "aplicaciones": aplicaciones})


@login_required
def cuenta_corriente(request, inscripcion_id):
    escuela = escuela_operativa(request)
    inscripcion = get_object_or_404(AlumnoEscuela.objects.select_related("alumno", "escuela"), pk=inscripcion_id, escuela=escuela)
    obligaciones = list(obligaciones_de_alumno(inscripcion))
    for obligacion in obligaciones:
        obligacion.estado_financiero = estado_obligacion(obligacion)
    resumen = {
        "facturado": sum((o.monto_original for o in obligaciones), 0),
        "pagado": sum((o.monto_pagado for o in obligaciones), 0),
        "saldo": sum((o.saldo for o in obligaciones), 0),
        "atrasadas": sum(1 for o in obligaciones if o.estado_financiero["temporal"] == "ATRASADA" and o.saldo > 0),
    }
    return render(request, "finanzas/cuenta_corriente.html", {"inscripcion": inscripcion, "obligaciones": obligaciones, "resumen": resumen})
