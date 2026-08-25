from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from ..forms import BloquearAccesoMobileAlumnoForm, GenerarCredencialesAlumnoForm, ResetearPasswordAlumnoForm
from ..models import AlumnoCredencial
from ..services import alumno_credencial_service
from ..services.excepciones import AlumnosError
from ._helpers import alumno_accesible, mensaje_error_validacion

def alumno_credencial_queryset(alumno):
    return AlumnoCredencial.objects.select_related("alumno", "usuario").filter(alumno=alumno)

@login_required
def alumno_credencial_generar(request, alumno_id):
    alumno, _ = alumno_accesible(request, alumno_id)
    if request.method == "POST":
        form = GenerarCredencialesAlumnoForm(request.POST)
        if form.is_valid():
            try: alumno_credencial_service.crear_credencial_mobile_para_alumno(alumno=alumno, password=form.cleaned_data["password"], password_confirmacion=form.cleaned_data["password_confirmacion"], actor=request.user)
            except AlumnosError as exc: mensaje_error_validacion(request, exc)
            else: messages.success(request, "Credenciales mobile generadas correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)

@login_required
def alumno_credencial_resetear_password(request, alumno_id):
    alumno, _ = alumno_accesible(request, alumno_id)
    credencial = get_object_or_404(alumno_credencial_queryset(alumno), alumno=alumno)
    if request.method == "POST":
        form = ResetearPasswordAlumnoForm(request.POST)
        if form.is_valid():
            try: alumno_credencial_service.resetear_password_credencial_mobile(credencial=credencial, password=form.cleaned_data["password"], password_confirmacion=form.cleaned_data["password_confirmacion"], actor=request.user)
            except AlumnosError as exc: mensaje_error_validacion(request, exc)
            else: messages.success(request, "Contrasena mobile actualizada correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)

@login_required
def alumno_credencial_revocar_sesiones(request, alumno_id):
    alumno, _ = alumno_accesible(request, alumno_id)
    credencial = get_object_or_404(alumno_credencial_queryset(alumno), alumno=alumno)
    if request.method == "POST":
        try:
            alumno_credencial_service.validar_acceso_gestion_credencial(actor=request.user, alumno=alumno)
            alumno_credencial_service.revocar_sesiones_mobile_alumno(usuario=credencial.usuario)
        except AlumnosError as exc: mensaje_error_validacion(request, exc)
        else: messages.success(request, "Sesiones mobile revocadas correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)

@login_required
def alumno_credencial_bloquear(request, alumno_id):
    alumno, _ = alumno_accesible(request, alumno_id)
    credencial = get_object_or_404(alumno_credencial_queryset(alumno), alumno=alumno)
    if request.method == "POST":
        form = BloquearAccesoMobileAlumnoForm(request.POST)
        if form.is_valid():
            try: alumno_credencial_service.bloquear_acceso_mobile(credencial=credencial, actor=request.user, motivo=form.cleaned_data["motivo"])
            except AlumnosError as exc: mensaje_error_validacion(request, exc)
            else: messages.success(request, "Acceso mobile bloqueado correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)

@login_required
def alumno_credencial_reactivar(request, alumno_id):
    alumno, _ = alumno_accesible(request, alumno_id)
    credencial = get_object_or_404(alumno_credencial_queryset(alumno), alumno=alumno)
    if request.method == "POST":
        try: alumno_credencial_service.reactivar_acceso_mobile(credencial=credencial, actor=request.user)
        except AlumnosError as exc: mensaje_error_validacion(request, exc)
        else: messages.success(request, "Acceso mobile reactivado correctamente.")
    return redirect("alumnos:alumno_detail", pk=alumno.pk)
