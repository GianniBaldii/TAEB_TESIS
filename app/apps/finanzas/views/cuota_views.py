from datetime import date
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import GenerarCuotasForm
from ..models import ConfiguracionCuota
from ..selectors import finanzas_selectors
from ..services import cuota_service
from ..services.excepciones import FinanzasError
from ._helpers import escuela_operativa, informar_error


@login_required
def cuota_list(request):
    escuela = escuela_operativa(request)
    hoy = date.today()
    anio = int(request.GET.get("anio", hoy.year))
    mes = int(request.GET.get("mes", hoy.month))
    clase_id = request.GET.get("clase")
    estado = request.GET.get("estado", "")
    clase = finanzas_selectors.clases_activas(escuela).filter(pk=clase_id).first() if clase_id else None
    items, resumen = finanzas_selectors.resumen_periodo(finanzas_selectors.obligaciones_de_periodo(escuela=escuela, anio=anio, mes=mes, clase=clase))
    if estado:
        items = [item for item in items if estado in item.estado_financiero.values()]
    return render(request, "finanzas/cuota_list.html", {"obligaciones": items, "resumen": resumen, "anio": anio, "mes": mes, "estado": estado, "clases": finanzas_selectors.clases_activas(escuela), "clase_seleccionada": clase})


@login_required
def generar_cuotas(request):
    escuela = escuela_operativa(request)
    configuracion = ConfiguracionCuota.objects.filter(escuela=escuela, activa=True).first()
    hoy = date.today()
    inicial = {"periodo": f"{hoy.year:04d}-{hoy.month:02d}", "destino": GenerarCuotasForm.Destino.TODOS}
    if configuracion:
        inicial.update({"monto": configuracion.monto_actual, "fecha_vencimiento": cuota_service.fecha_vencimiento_periodo(hoy.year, hoy.month, configuracion.dia_vencimiento), "dias_tolerancia": configuracion.dias_tolerancia})
    form = GenerarCuotasForm(request.POST or None, escuela=escuela, initial=inicial)
    if request.method == "POST" and form.is_valid():
        anio, mes = map(int, form.cleaned_data["periodo"].split("-"))
        destino = form.cleaned_data["destino"]
        if destino == GenerarCuotasForm.Destino.CLASE:
            inscripciones = finanzas_selectors.alumnos_de_clase(form.cleaned_data["clase"])
        elif destino == GenerarCuotasForm.Destino.MANUAL:
            inscripciones = form.cleaned_data["alumnos"]
        else:
            inscripciones = finanzas_selectors.alumnos_activos(escuela)
        try:
            resultado = cuota_service.generar_cuotas_periodo(escuela=escuela, alumnos_escuela=inscripciones, anio=anio, mes=mes, monto=form.cleaned_data["monto"], fecha_vencimiento=form.cleaned_data["fecha_vencimiento"], dias_tolerancia=form.cleaned_data["dias_tolerancia"], usuario=request.user)
        except FinanzasError as exc:
            informar_error(request, exc)
        else:
            messages.success(request, f"Se generaron {len(resultado['creadas'])} cuotas; {len(resultado['omitidas'])} ya existían.")
            return redirect(f"/finanzas/cuotas/?anio={anio}&mes={mes}")
    seleccionados = request.POST.getlist("alumnos") if request.method == "POST" else []
    return render(request, "finanzas/generar_cuotas.html", {
        "form": form,
        "configuracion": configuracion,
        "alumnos_disponibles": form.fields["alumnos"].queryset,
        "alumnos_ids_json": json.dumps([str(pk) for pk in form.fields["alumnos"].queryset.values_list("pk", flat=True)]),
        "alumnos_seleccionados_json": json.dumps(seleccionados),
        "destino_inicial_json": json.dumps(request.POST.get("destino", GenerarCuotasForm.Destino.TODOS)),
    })
