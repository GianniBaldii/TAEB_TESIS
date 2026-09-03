from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from apps.usuarios.models import Docente
from apps.usuarios.services import docente_service
from ..decorators import requerir_superadmin
from ..forms import DocenteAltaForm, DocenteEscuelaForm, ResetearPasswordDocenteForm
from ..selectors import docente_escuela_selectors
from ..services import docente_escuela_service
from ..services.excepciones import EscuelasError

@requerir_superadmin
def docente_create(request):
    form = DocenteAltaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            docente_service.crear_docente_con_usuario_y_escuela(
                {"username": form.cleaned_data["username"], "first_name": form.cleaned_data["first_name"], "last_name": form.cleaned_data["last_name"], "email": form.cleaned_data["email"], "password": form.cleaned_data["password1"]},
                {"dni": form.cleaned_data["dni"], "telefono": form.cleaned_data["telefono"], "fecha_nacimiento": form.cleaned_data["fecha_nacimiento"]},
                form.cleaned_data["escuela"], form.cleaned_data["rol"],
            )
        except EscuelasError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
        else:
            messages.success(request, "Docente creado correctamente.")
            return redirect("escuelas:docente_list")
    return render(request, "escuelas/docente_form.html", {"form": form})

@requerir_superadmin
def docente_list(request):
    docentes = docente_escuela_selectors.docentes_para_listado()
    return render(request, "escuelas/docente_list.html", {"docentes": docentes, "docentes_activos": docentes.filter(activo=True).count()})

@requerir_superadmin
def docente_detail(request, pk):
    docente = get_object_or_404(docente_escuela_selectors.docentes_para_listado(), pk=pk)
    return render(request, "escuelas/docente_detail.html", {"docente": docente, "resetear_password_form": ResetearPasswordDocenteForm(usuario=docente.usuario)})


@requerir_superadmin
def docente_resetear_password(request, pk):
    docente = get_object_or_404(Docente.objects.select_related("usuario"), pk=pk)
    if request.method == "POST":
        form = ResetearPasswordDocenteForm(request.POST, usuario=docente.usuario)
        if form.is_valid():
            docente_service.resetear_password_docente(docente, form.cleaned_data["password1"])
            messages.success(request, f"Contraseña de {docente} actualizada correctamente.")
        else:
            for errores in form.errors.values():
                for error in errores:
                    messages.error(request, error, extra_tags="validation_error")
    return redirect("escuelas:docente_detail", pk=docente.pk)

@requerir_superadmin
def docente_estado(request, pk, activar):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == "POST":
        (docente_service.reactivar_docente if activar else docente_service.desactivar_docente)(docente)
        messages.success(request, "Docente actualizado correctamente.")
    return redirect("escuelas:docente_detail", pk=docente.pk)

@requerir_superadmin
def docente_escuela_create(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    form = DocenteEscuelaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            docente_escuela_service.vincular_docente_a_escuela(docente, form.cleaned_data["escuela"], form.cleaned_data["rol"])
        except EscuelasError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
        else:
            messages.success(request, "Escuela asociada correctamente.")
            return redirect("escuelas:docente_detail", pk=docente.pk)
    return render(request, "escuelas/docente_escuela_form.html", {"form": form, "docente": docente})

@requerir_superadmin
def docente_escuela_estado(request, pk, activar):
    relacion = get_object_or_404(docente_escuela_selectors.relaciones_con_detalle(), pk=pk)
    if request.method == "POST":
        try:
            docente_escuela_service.cambiar_estado_relacion(relacion, activar)
        except EscuelasError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
    return redirect("escuelas:docente_detail", pk=relacion.docente_id)
