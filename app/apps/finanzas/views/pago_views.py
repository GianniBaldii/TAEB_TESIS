from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from ..forms import PagoForm
from ..services.excepciones import FinanzasError
from ..services.pago_service import registrar_pago as registrar_pago_service
from ._helpers import informar_error, obligacion_accesible


@login_required
def registrar_pago(request, pk):
    obligacion = obligacion_accesible(request, pk)
    form = PagoForm(request.POST or None, initial={"monto": obligacion.saldo, "fecha_pago": timezone.localdate()})
    if request.method == "POST" and form.is_valid():
        try:
            registrar_pago_service(obligacion=obligacion, usuario=request.user, **form.cleaned_data)
        except FinanzasError as exc:
            informar_error(request, exc)
        else:
            messages.success(request, "Pago registrado correctamente.")
            return redirect("finanzas:obligacion_detail", pk=pk)
    return render(request, "finanzas/pago_form.html", {"form": form, "obligacion": obligacion})
