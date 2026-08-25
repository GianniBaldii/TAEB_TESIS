from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from ..decorators import requerir_superadmin
from ..forms import EscuelaForm
from ..models import Escuela
from ..selectors import escuela_selectors
from ..services import escuela_service
from ..services.excepciones import EscuelasError

@requerir_superadmin
def escuela_list(request):
    escuelas = escuela_selectors.escuelas_para_listado()
    return render(request, "escuelas/escuela_list.html", {"escuelas": escuelas, "escuelas_activas": escuelas.filter(activo=True).count()})

@requerir_superadmin
def escuela_create(request):
    form = EscuelaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        escuela_service.crear_escuela(form.cleaned_data)
        messages.success(request, "Escuela creada correctamente.")
        return redirect("escuelas:escuela_list")
    return render(request, "escuelas/escuela_form.html", {"form": form, "modo": "crear"})

@requerir_superadmin
def escuela_update(request, pk):
    escuela = get_object_or_404(Escuela, pk=pk)
    form = EscuelaForm(request.POST or None, instance=escuela)
    if request.method == "POST" and form.is_valid():
        try: escuela_service.actualizar_escuela(escuela, form.cleaned_data)
        except EscuelasError as exc: messages.error(request, str(exc), extra_tags="validation_error")
        else:
            messages.success(request, "Escuela actualizada correctamente.")
            return redirect("escuelas:escuela_list")
    return render(request, "escuelas/escuela_form.html", {"form": form, "modo": "editar", "escuela": escuela})

@requerir_superadmin
def escuela_estado(request, pk, activar):
    escuela = get_object_or_404(Escuela, pk=pk)
    if request.method == "POST":
        (escuela_service.activar_escuela if activar else escuela_service.desactivar_escuela)(escuela)
        messages.success(request, "Escuela actualizada correctamente.")
    return redirect("escuelas:escuela_list")
