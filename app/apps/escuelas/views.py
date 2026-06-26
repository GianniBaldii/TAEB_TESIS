from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.escuelas.decorators import requerir_superadmin
from apps.escuelas.forms import DocenteAltaForm, DocenteEscuelaForm, EscuelaForm
from apps.escuelas.models import Escuela, EscuelaDocente
from apps.escuelas.services import escuela_service
from apps.escuelas.services.excepciones import EscuelasError
from apps.usuarios.services import docente_service


@requerir_superadmin
def escuela_list(request):
    escuelas = Escuela.objects.all()
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
        try:
            escuela_service.actualizar_escuela(escuela, form.cleaned_data)
        except EscuelasError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
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


@requerir_superadmin
def docente_create(request):
    form = DocenteAltaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            docente = docente_service.crear_docente_con_usuario_y_escuela(
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
    from apps.usuarios.models import Docente
    docentes = Docente.objects.select_related("usuario").prefetch_related("escuelas__escuela")
    return render(request, "escuelas/docente_list.html", {"docentes": docentes, "docentes_activos": docentes.filter(activo=True).count()})


@requerir_superadmin
def docente_detail(request, pk):
    from apps.usuarios.models import Docente
    docente = get_object_or_404(Docente.objects.select_related("usuario").prefetch_related("escuelas__escuela"), pk=pk)
    return render(request, "escuelas/docente_detail.html", {"docente": docente})


@requerir_superadmin
def docente_estado(request, pk, activar):
    from apps.usuarios.models import Docente
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == "POST":
        (docente_service.reactivar_docente if activar else docente_service.desactivar_docente)(docente)
        messages.success(request, "Docente actualizado correctamente.")
    return redirect("escuelas:docente_detail", pk=docente.pk)


@requerir_superadmin
def docente_escuela_create(request, pk):
    from apps.usuarios.models import Docente
    docente = get_object_or_404(Docente, pk=pk)
    form = DocenteEscuelaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            docente_service.vincular_docente_a_escuela(docente, form.cleaned_data["escuela"], form.cleaned_data["rol"])
        except EscuelasError as exc:
            messages.error(request, str(exc), extra_tags="validation_error")
        else:
            messages.success(request, "Escuela asociada correctamente.")
            return redirect("escuelas:docente_detail", pk=docente.pk)
    return render(request, "escuelas/docente_escuela_form.html", {"form": form, "docente": docente})


@requerir_superadmin
def docente_escuela_estado(request, pk, activar):
    relacion = get_object_or_404(EscuelaDocente.objects.select_related("docente", "escuela"), pk=pk)
    if request.method == "POST":
        if activar:
            if not relacion.docente.activo or not relacion.escuela.activo:
                messages.error(request, "El docente y la escuela deben estar activos.", extra_tags="validation_error")
            else:
                relacion.activo, relacion.fecha_baja = True, None
                relacion.save(update_fields=["activo", "fecha_baja"])
        else:
            from django.utils import timezone
            relacion.activo, relacion.fecha_baja = False, timezone.localdate()
            relacion.save(update_fields=["activo", "fecha_baja"])
    return redirect("escuelas:docente_detail", pk=relacion.docente_id)
