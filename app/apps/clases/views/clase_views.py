from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from apps.escuelas.models import Escuela
from ..forms import ClaseForm
from ..services import clase_service
from ..services.excepciones import ClasesError
from ._helpers import clase_accesible, clase_queryset, escuela_operativa, mensaje_error_validacion

@login_required
def clase_list(request):
    clases = clase_queryset(request).annotate(alumnos_activos=Count("inscripciones_alumnos", filter=Q(inscripciones_alumnos__activo=True), distinct=True))
    escuela_id, activo = request.GET.get("escuela", ""), request.GET.get("activo", "")
    if request.user.is_superuser and escuela_id: clases = clases.filter(escuela_id=escuela_id)
    if activo in {"1", "0"}: clases = clases.filter(activo=activo == "1")
    return render(request, "clases/clase_list.html", {"clases": clases.prefetch_related("horarios"), "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else [], "filtros": {"escuela": escuela_id, "activo": activo}})

@login_required
def clase_create(request):
    escuela = None if request.user.is_superuser else escuela_operativa(request)
    form = ClaseForm(request.POST or None, escuela=escuela, permitir_escuela=request.user.is_superuser)
    if request.method == "POST" and form.is_valid():
        if request.user.is_superuser: escuela = form.cleaned_data["escuela"]
        try: clase = clase_service.crear_clase(escuela, form.cleaned_data)
        except ClasesError as exc: mensaje_error_validacion(request, exc)
        else: messages.success(request, "Clase creada correctamente."); return redirect("clases:clase_detail", clase_id=clase.pk)
    return render(request, "clases/clase_form.html", {"form": form, "modo": "crear", "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else []})

@login_required
def clase_update(request, clase_id):
    clase = clase_accesible(request, clase_id); form = ClaseForm(request.POST or None, instance=clase, escuela=clase.escuela, permitir_escuela=False)
    if request.method == "POST" and form.is_valid():
        try: clase_service.actualizar_clase(clase, form.cleaned_data)
        except ClasesError as exc: mensaje_error_validacion(request, exc)
        else: messages.success(request, "Clase actualizada correctamente."); return redirect("clases:clase_detail", clase_id=clase.pk)
    return render(request, "clases/clase_form.html", {"form": form, "modo": "editar", "clase": clase})

@login_required
def clase_detail(request, clase_id):
    clase = clase_accesible(request, clase_id)
    return render(request, "clases/clase_detail.html", {"clase": clase, "horarios": clase.horarios.all(), "inscripciones": clase.inscripciones_alumnos.select_related("alumno_escuela__alumno", "alumno_escuela__alumno__cinturon_actual"), "sesiones": clase.sesiones.order_by("-fecha", "-hora_inicio")[:8]})

@login_required
def clase_estado(request, clase_id, activar):
    clase = clase_accesible(request, clase_id)
    if request.method == "POST": (clase_service.activar_clase if activar else clase_service.desactivar_clase)(clase); messages.success(request, "Clase actualizada correctamente.")
    return redirect("clases:clase_detail", clase_id=clase.pk)
