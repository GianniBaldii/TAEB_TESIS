from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from apps.escuelas.models import Escuela, EscuelaDocente
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario

from .forms import (
    CancelarSesionForm,
    ClaseAlumnoForm,
    ClaseExtraForm,
    ClaseForm,
    ClaseHorarioForm,
)
from .models import AsistenciaClase, Clase, ClaseAlumno, ClaseHorario, ClaseSesion
from .services import (
    asistencia_service,
    clase_alumno_service,
    clase_horario_service,
    clase_service,
    clase_sesion_service,
)
from .services.excepciones import ClasesError


def _mensaje_error_validacion(request, error):
    messages.error(request, str(error), extra_tags="validation_error")


def _escuela_operativa(request):
    return obtener_escuela_activa_usuario(request.user)


def _escuelas_visibles(request):
    if request.user.is_superuser:
        return Escuela.objects.filter(activo=True)
    return Escuela.objects.filter(pk=_escuela_operativa(request).pk)


def _clase_queryset(request):
    clases = Clase.objects.select_related(
        "escuela",
        "docente_responsable",
        "docente_responsable__docente__usuario",
    )
    if request.user.is_superuser:
        return clases
    return clases.filter(escuela=_escuela_operativa(request))


def _clase_accesible(request, clase_id):
    clase = get_object_or_404(_clase_queryset(request), pk=clase_id)
    clase_service.validar_acceso_clase(request.user, clase)
    return clase


def _horario_accesible(request, horario_id):
    horario = get_object_or_404(
        ClaseHorario.objects.select_related("clase", "clase__escuela"),
        pk=horario_id,
    )
    clase_service.validar_acceso_clase(request.user, horario.clase)
    return horario


def _sesion_accesible(request, sesion_id):
    sesion = get_object_or_404(
        ClaseSesion.objects.select_related(
            "clase",
            "clase__escuela",
            "docente_a_cargo",
            "docente_a_cargo__docente__usuario",
        ),
        pk=sesion_id,
    )
    clase_service.validar_acceso_clase(request.user, sesion.clase)
    return sesion


def _rango_calendario(request):
    fecha_base = parse_date(request.GET.get("fecha", "")) or date.today()
    vista = request.GET.get("vista", "semana")
    if vista == "dia":
        return fecha_base, fecha_base, "dia"
    inicio = fecha_base - timedelta(days=fecha_base.weekday())
    return inicio, inicio + timedelta(days=6), "semana"


@login_required
def clase_list(request):
    clases = _clase_queryset(request).annotate(
        alumnos_activos=Count(
            "inscripciones_alumnos",
            filter=Q(inscripciones_alumnos__activo=True),
            distinct=True,
        )
    )
    escuela_id = request.GET.get("escuela", "")
    if request.user.is_superuser and escuela_id:
        clases = clases.filter(escuela_id=escuela_id)
    activo = request.GET.get("activo", "")
    if activo in {"1", "0"}:
        clases = clases.filter(activo=activo == "1")
    return render(
        request,
        "clases/clase_list.html",
        {
            "clases": clases.prefetch_related("horarios"),
            "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else [],
            "filtros": {"escuela": escuela_id, "activo": activo},
        },
    )


@login_required
def clase_create(request):
    escuela = None if request.user.is_superuser else _escuela_operativa(request)
    form = ClaseForm(
        request.POST or None,
        escuela=escuela,
        permitir_escuela=request.user.is_superuser,
    )
    if request.method == "POST" and form.is_valid():
        if request.user.is_superuser:
            escuela = form.cleaned_data["escuela"]
        try:
            clase = clase_service.crear_clase(escuela, form.cleaned_data)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Clase creada correctamente.")
            return redirect("clases:clase_detail", clase_id=clase.pk)
    return render(
        request,
        "clases/clase_form.html",
        {
            "form": form,
            "modo": "crear",
            "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else [],
        },
    )


@login_required
def clase_update(request, clase_id):
    clase = _clase_accesible(request, clase_id)
    form = ClaseForm(
        request.POST or None,
        instance=clase,
        escuela=clase.escuela,
        permitir_escuela=False,
    )
    if request.method == "POST" and form.is_valid():
        try:
            clase_service.actualizar_clase(clase, form.cleaned_data)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Clase actualizada correctamente.")
            return redirect("clases:clase_detail", clase_id=clase.pk)
    return render(
        request,
        "clases/clase_form.html",
        {"form": form, "modo": "editar", "clase": clase},
    )


@login_required
def clase_detail(request, clase_id):
    clase = _clase_accesible(request, clase_id)
    horarios = clase.horarios.all()
    inscripciones = clase.inscripciones_alumnos.select_related(
        "alumno_escuela__alumno",
        "alumno_escuela__alumno__cinturon_actual",
    )
    sesiones = clase.sesiones.order_by("-fecha", "-hora_inicio")[:8]
    return render(
        request,
        "clases/clase_detail.html",
        {
            "clase": clase,
            "horarios": horarios,
            "inscripciones": inscripciones,
            "sesiones": sesiones,
        },
    )


@login_required
def clase_estado(request, clase_id, activar):
    clase = _clase_accesible(request, clase_id)
    if request.method == "POST":
        (clase_service.activar_clase if activar else clase_service.desactivar_clase)(clase)
        messages.success(request, "Clase actualizada correctamente.")
    return redirect("clases:clase_detail", clase_id=clase.pk)


@login_required
def horario_create(request, clase_id):
    clase = _clase_accesible(request, clase_id)
    form = ClaseHorarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            clase_horario_service.crear_horario_clase(clase, form.cleaned_data)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Horario agregado correctamente.")
            return redirect("clases:clase_detail", clase_id=clase.pk)
    return render(request, "clases/horario_form.html", {"form": form, "clase": clase})


@login_required
def horario_update(request, horario_id):
    horario = _horario_accesible(request, horario_id)
    form = ClaseHorarioForm(request.POST or None, instance=horario)
    if request.method == "POST" and form.is_valid():
        try:
            clase_horario_service.actualizar_horario_clase(horario, form.cleaned_data)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Horario actualizado correctamente.")
            return redirect("clases:clase_detail", clase_id=horario.clase_id)
    return render(
        request,
        "clases/horario_form.html",
        {"form": form, "clase": horario.clase, "horario": horario},
    )


@login_required
def horario_desactivar(request, horario_id):
    horario = _horario_accesible(request, horario_id)
    if request.method == "POST":
        clase_horario_service.desactivar_horario_clase(horario)
        messages.success(request, "Horario desactivado correctamente.")
    return redirect("clases:clase_detail", clase_id=horario.clase_id)


@login_required
def clase_alumno_create(request, clase_id):
    clase = _clase_accesible(request, clase_id)
    alumnos = clase_alumno_service.obtener_alumnos_disponibles_para_clase(
        clase,
        request.GET.get("q", "").strip(),
    )
    form = ClaseAlumnoForm(request.POST or None, alumnos_queryset=alumnos)
    if request.method == "POST" and form.is_valid():
        try:
            clase_alumno_service.inscribir_alumno_en_clase(
                clase,
                form.cleaned_data["alumno_escuela"],
                form.cleaned_data["observaciones"],
            )
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Alumno inscripto correctamente.")
            return redirect("clases:clase_detail", clase_id=clase.pk)
    return render(
        request,
        "clases/clase_alumno_form.html",
        {"form": form, "clase": clase, "busqueda": request.GET.get("q", "")},
    )


@login_required
def clase_alumno_baja(request, clase_alumno_id):
    inscripcion = get_object_or_404(
        ClaseAlumno.objects.select_related("clase", "clase__escuela"),
        pk=clase_alumno_id,
    )
    clase_service.validar_acceso_clase(request.user, inscripcion.clase)
    if request.method == "POST":
        clase_alumno_service.dar_baja_alumno_de_clase(inscripcion)
        messages.success(request, "Alumno dado de baja de la clase.")
    return redirect("clases:clase_detail", clase_id=inscripcion.clase_id)


@login_required
def clase_alumno_reactivar(request, clase_alumno_id):
    inscripcion = get_object_or_404(
        ClaseAlumno.objects.select_related(
            "clase",
            "clase__escuela",
            "alumno_escuela",
            "alumno_escuela__alumno",
        ),
        pk=clase_alumno_id,
    )
    clase_service.validar_acceso_clase(request.user, inscripcion.clase)
    if request.method == "POST":
        try:
            clase_alumno_service.reactivar_alumno_en_clase(inscripcion)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Inscripcion reactivada correctamente.")
    return redirect("clases:clase_detail", clase_id=inscripcion.clase_id)


@login_required
def calendario(request):
    fecha_desde, fecha_hasta, vista = _rango_calendario(request)
    escuela_id = request.GET.get("escuela", "")
    clase_id = request.GET.get("clase", "")
    docente_id = request.GET.get("docente", "")
    escuelas = _escuelas_visibles(request)
    if request.user.is_superuser and escuela_id:
        escuelas = escuelas.filter(pk=escuela_id)
    clases_filtro = _clase_queryset(request).filter(escuela__in=escuelas, activo=True)
    docentes_filtro = EscuelaDocente.objects.select_related(
        "docente__usuario",
        "escuela",
    ).filter(escuela__in=escuelas, activo=True, docente__activo=True)
    ocurrencias = []
    sesiones = []
    for escuela in escuelas:
        ocurrencias.extend(
            clase_horario_service.obtener_ocurrencias_calendario(
                escuela, fecha_desde, fecha_hasta
            )
        )
        sesiones.extend(
            clase_sesion_service.obtener_sesiones_calendario(
                escuela, fecha_desde, fecha_hasta
            )
        )
    if clase_id:
        ocurrencias = [
            ocurrencia
            for ocurrencia in ocurrencias
            if str(ocurrencia["clase"].pk) == clase_id
        ]
        sesiones = [sesion for sesion in sesiones if str(sesion.clase_id) == clase_id]
    if docente_id:
        ocurrencias = [
            ocurrencia
            for ocurrencia in ocurrencias
            if str(ocurrencia["clase"].docente_responsable_id) == docente_id
        ]
        sesiones = [
            sesion
            for sesion in sesiones
            if str(sesion.docente_a_cargo_id or sesion.clase.docente_responsable_id)
            == docente_id
        ]
    sesiones_por_clave = {
        (sesion.clase_id, sesion.fecha, sesion.hora_inicio): sesion for sesion in sesiones
    }
    eventos = []
    for ocurrencia in ocurrencias:
        clave = (
            ocurrencia["clase"].pk,
            ocurrencia["fecha"],
            ocurrencia["hora_inicio"],
        )
        if clave not in sesiones_por_clave:
            eventos.append(ocurrencia)
    eventos.extend({"tipo": "sesion", "sesion": sesion} for sesion in sesiones)
    eventos = sorted(
        eventos,
        key=lambda item: (
            item["sesion"].fecha if item["tipo"] == "sesion" else item["fecha"],
            item["sesion"].hora_inicio if item["tipo"] == "sesion" else item["hora_inicio"],
        ),
    )
    return render(
        request,
        "clases/calendario.html",
        {
            "eventos": eventos,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "fecha_anterior": fecha_desde - timedelta(days=1 if vista == "dia" else 7),
            "fecha_siguiente": fecha_hasta + timedelta(days=1),
            "vista": vista,
            "escuelas": Escuela.objects.filter(activo=True) if request.user.is_superuser else [],
            "clases": clases_filtro,
            "docentes": docentes_filtro,
            "filtros": {
                "escuela": escuela_id,
                "clase": clase_id,
                "docente": docente_id,
            },
        },
    )


@login_required
def abrir_ocurrencia(request, horario_id):
    horario = _horario_accesible(request, horario_id)
    fecha = parse_date(request.GET.get("fecha", ""))
    if not fecha:
        _mensaje_error_validacion(request, "Fecha invalida para abrir la sesion.")
        return redirect("clases:calendario")
    try:
        sesion = clase_sesion_service.crear_o_obtener_sesion(
            horario.clase,
            horario,
            fecha,
        )
    except ClasesError as exc:
        _mensaje_error_validacion(request, exc)
        return redirect("clases:calendario")
    return redirect("clases:sesion_detail", sesion_id=sesion.pk)


@login_required
def clase_extra_create(request, clase_id):
    clase = _clase_accesible(request, clase_id)
    form = ClaseExtraForm(request.POST or None, escuela=clase.escuela)
    if request.method == "POST" and form.is_valid():
        try:
            sesion = clase_sesion_service.crear_clase_extra(
                clase=clase,
                fecha=form.cleaned_data["fecha"],
                hora_inicio=form.cleaned_data["hora_inicio"],
                hora_fin=form.cleaned_data["hora_fin"],
                docente_a_cargo=form.cleaned_data["docente_a_cargo"],
                observaciones=form.cleaned_data["observaciones"],
            )
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Clase extra creada correctamente.")
            return redirect("clases:sesion_detail", sesion_id=sesion.pk)
    return render(request, "clases/clase_extra_form.html", {"form": form, "clase": clase})


@login_required
def sesion_detail(request, sesion_id):
    sesion = _sesion_accesible(request, sesion_id)
    resumen = asistencia_service.obtener_resumen_asistencia_sesion(sesion)
    return render(
        request,
        "clases/sesion_detail.html",
        {"sesion": sesion, "resumen": resumen},
    )


@login_required
def asistencia_form(request, sesion_id):
    sesion = _sesion_accesible(request, sesion_id)
    if request.method == "POST":
        datos = {}
        for clave, valor in request.POST.items():
            if clave.startswith("estado_"):
                asistencia_id = clave.replace("estado_", "")
                datos[asistencia_id] = {
                    "estado": valor,
                    "observaciones": request.POST.get(f"observaciones_{asistencia_id}", ""),
                }
        try:
            asistencia_service.guardar_asistencias_sesion(sesion, datos, request.user)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Asistencia guardada correctamente.")
            return redirect("clases:asistencia_form", sesion_id=sesion.pk)
    try:
        asistencias = asistencia_service.inicializar_asistencias_sesion(sesion, request.user)
    except ClasesError as exc:
        _mensaje_error_validacion(request, exc)
        asistencias = sesion.asistencias.select_related(
            "clase_alumno__alumno_escuela__alumno",
            "clase_alumno__alumno_escuela__alumno__cinturon_actual",
        )
    return render(
        request,
        "clases/asistencia_form.html",
        {
            "sesion": sesion,
            "asistencias": asistencias,
            "estados": AsistenciaClase.Estado.choices,
        },
    )


@login_required
def marcar_todos_presentes(request, sesion_id):
    sesion = _sesion_accesible(request, sesion_id)
    if request.method == "POST":
        try:
            asistencia_service.marcar_todos_presentes(sesion, request.user)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Todos los alumnos fueron marcados presentes.")
    return redirect("clases:asistencia_form", sesion_id=sesion.pk)


@login_required
def cerrar_asistencia(request, sesion_id):
    sesion = _sesion_accesible(request, sesion_id)
    if request.method == "POST":
        try:
            asistencia_service.cerrar_asistencia_sesion(sesion, request.user)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Asistencia cerrada correctamente.")
    return redirect("clases:sesion_detail", sesion_id=sesion.pk)


@login_required
def reabrir_asistencia(request, sesion_id):
    sesion = _sesion_accesible(request, sesion_id)
    if request.method == "POST":
        try:
            asistencia_service.reabrir_asistencia_sesion(sesion, request.user)
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Asistencia reabierta correctamente.")
    return redirect("clases:asistencia_form", sesion_id=sesion.pk)


@login_required
def cancelar_sesion(request, sesion_id):
    sesion = _sesion_accesible(request, sesion_id)
    form = CancelarSesionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            clase_sesion_service.cancelar_sesion(sesion, form.cleaned_data["motivo"])
        except ClasesError as exc:
            _mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Sesion cancelada correctamente.")
            return redirect("clases:sesion_detail", sesion_id=sesion.pk)
    return render(request, "clases/cancelar_sesion_form.html", {"form": form, "sesion": sesion})
