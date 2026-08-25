from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from apps.escuelas.models import Escuela
from ..forms import AlumnoForm, BloquearAccesoMobileAlumnoForm, GenerarCredencialesAlumnoForm, ResetearPasswordAlumnoForm
from ..models import Cinturon, Examen
from ..selectors import alumno_selectors
from ..services import alumno_service, trayectoria_taekwondista_service
from ..services.excepciones import AlumnosError
from ._helpers import alumno_accesible, escuela_operativa, examen_queryset, mensaje_error_validacion

@login_required
def alumno_list(request):
    inscripciones = alumno_selectors.inscripciones_visibles_para_usuario(request.user, incluir_inactivas=True)
    escuela_id, busqueda = request.GET.get("escuela", ""), request.GET.get("q", "").strip()
    activo, cinturon_id = request.GET.get("activo", ""), request.GET.get("cinturon", "")
    if request.user.is_superuser and escuela_id: inscripciones = inscripciones.filter(escuela_id=escuela_id)
    if busqueda:
        inscripciones = inscripciones.filter(Q(alumno__nombre__icontains=busqueda) | Q(alumno__apellido__icontains=busqueda) | Q(alumno__dni__icontains=busqueda))
    if activo in {"1", "0"}: inscripciones = inscripciones.filter(activo=activo == "1")
    if cinturon_id: inscripciones = inscripciones.filter(alumno__cinturon_actual_id=cinturon_id)
    return render(request, "alumnos/alumno_list.html", {"inscripciones": inscripciones, "alumnos": [i.alumno for i in inscripciones], "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else [], "cinturones": Cinturon.objects.filter(activo=True), "filtros": {"q": busqueda, "activo": activo, "cinturon": cinturon_id, "escuela": escuela_id}, "titulo_pagina": "Alumnos"})

@login_required
def alumno_create(request):
    form = AlumnoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        escuela = escuela_operativa(request)
        if request.user.is_superuser: escuela = get_object_or_404(Escuela.objects.filter(activo=True), pk=request.POST.get("escuela"))
        try: alumno, _ = alumno_service.crear_alumno_e_inscribir_en_escuela(form.cleaned_data, escuela)
        except AlumnosError as exc: mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Alumno creado e inscripto correctamente.")
            return redirect("alumnos:alumno_detail", pk=alumno.pk)
    return render(request, "alumnos/alumno_form.html", {"form": form, "modo": "crear", "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else []})

@login_required
def alumno_update(request, pk):
    alumno, _ = alumno_accesible(request, pk)
    form = AlumnoForm(request.POST or None, instance=alumno)
    if request.method == "POST" and form.is_valid():
        alumno_service.actualizar_alumno(alumno, form.cleaned_data)
        messages.success(request, "Alumno actualizado correctamente.")
        return redirect("alumnos:alumno_detail", pk=alumno.pk)
    return render(request, "alumnos/alumno_form.html", {"form": form, "alumno": alumno, "modo": "editar"})

@login_required
def alumno_detail(request, pk):
    # La ficha también es el punto de entrada para reactivar una inscripción.
    # El acceso sigue limitado a la escuela visible del usuario, pero no al estado.
    alumno, inscripcion = alumno_accesible(request, pk, incluir_inactiva=True)
    return render(request, "alumnos/alumno_detail.html", {"alumno": alumno, "inscripcion": inscripcion, "credencial_mobile": getattr(alumno, "credencial_mobile", None), "generar_credenciales_form": GenerarCredencialesAlumnoForm(), "resetear_password_form": ResetearPasswordAlumnoForm(), "bloquear_acceso_form": BloquearAccesoMobileAlumnoForm(), "progreso": alumno_service.obtener_progreso_alumno(alumno), "analisis_trayectoria": trayectoria_taekwondista_service.obtener_analisis_trayectoria(alumno), "examenes": examen_queryset(alumno).exclude(estado=Examen.Estado.ANULADO), "historial": alumno.historial_cinturones.select_related("cinturon", "examen")})

@login_required
def alumno_baja(request, pk):
    alumno, inscripcion = alumno_accesible(request, pk, incluir_inactiva=True)
    if request.method == "POST":
        alumno_service.dar_baja_inscripcion(inscripcion); messages.success(request, "Inscripción del alumno dada de baja correctamente.")
    return redirect("alumnos:alumno_list")

@login_required
def alumno_reactivar(request, pk):
    alumno, inscripcion = alumno_accesible(request, pk, incluir_inactiva=True)
    if request.method == "POST":
        alumno_service.reactivar_inscripcion(inscripcion); messages.success(request, "Inscripción del alumno reactivada correctamente.")
    return redirect("alumnos:alumno_list")
