from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import GenerarCobroForm
from ..services.excepciones import FinanzasError
from ..services.obligacion_service import crear_obligaciones
from ._helpers import escuela_operativa, informar_error


@login_required
def generar_cobro(request):
    escuela = escuela_operativa(request)
    form = GenerarCobroForm(request.POST or None, escuela=escuela)
    if request.method == "POST" and form.is_valid():
        try:
            resultado = crear_obligaciones(escuela=escuela, concepto=form.cleaned_data["concepto"], alumnos_escuela=form.cleaned_data["alumnos"], monto=form.cleaned_data["monto"], fecha_vencimiento=form.cleaned_data["fecha_vencimiento"], dias_tolerancia=form.cleaned_data["dias_tolerancia"], descripcion=form.cleaned_data["descripcion"], usuario=request.user)
        except FinanzasError as exc:
            informar_error(request, exc)
        else:
            messages.success(request, f"Se generaron {len(resultado['creadas'])} cobros.")
            return redirect("finanzas:cuota_list")
    return render(request, "finanzas/generar_cobro.html", {"form": form})
