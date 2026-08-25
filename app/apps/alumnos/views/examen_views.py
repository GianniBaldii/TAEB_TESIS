from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import CrearExamenForm
from ..services import alumno_service, examen_alumno_service
from ..services.excepciones import AlumnosError
from ._helpers import alumno_accesible, examen_queryset, mensaje_error_validacion

def _obtener_examen(request, alumno_id, examen_id):
    alumno, _ = alumno_accesible(request, alumno_id)
    return alumno, get_object_or_404(examen_queryset(alumno), pk=examen_id)

@login_required
def examen_create(request, alumno_id):
    alumno, _ = alumno_accesible(request, alumno_id); form = CrearExamenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try: examen = examen_alumno_service.crear_examen_para_alumno(alumno=alumno, fecha_examen=form.cleaned_data["fecha_examen"], lugar=form.cleaned_data["lugar"], cinturon_destino=form.cleaned_data["cinturon_destino"], es_historico=form.cleaned_data["es_historico"])
        except AlumnosError as exc: mensaje_error_validacion(request, exc)
        else:
            messages.success(request, "Examen creado correctamente."); return redirect("alumnos:examen_evaluaciones", alumno_id=alumno.pk, examen_id=examen.pk)
    return render(request, "alumnos/examenes/examen_form.html", {"form": form, "alumno": alumno, "proximo_cinturon": alumno_service.obtener_siguiente_cinturon(alumno.cinturon_actual)})

@login_required
def examen_detail(request, alumno_id, examen_id):
    alumno, examen = _obtener_examen(request, alumno_id, examen_id)
    return render(request, "alumnos/examenes/examen_detail.html", {"alumno": alumno, "examen": examen, "detalles": examen.detalles.select_related("template_item", "template_item__seccion")})

@login_required
def examen_evaluaciones(request, alumno_id, examen_id):
    alumno, examen = _obtener_examen(request, alumno_id, examen_id)
    if examen_alumno_service.examen_tiene_estado_final(examen):
        mensaje_error_validacion(request, "No se pueden editar evaluaciones de un examen con estado final."); return redirect("alumnos:examen_detail", alumno_id=alumno.pk, examen_id=examen.pk)
    detalles = examen.detalles.select_related("template_item", "template_item__seccion")
    if request.method == "POST":
        data = {"detalles": {}}
        for detalle in detalles:
            base = f"detalle_{detalle.pk}_"
            data["detalles"][detalle.pk] = {campo: request.POST.get(base + campo) for campo in ("nota_numerica", "concepto", "valor_texto", "aprobado", "observaciones")}
        data.update({campo: request.POST.get(campo) for campo in ("nota_final", "resultado_final", "observaciones")})
        try: examen_alumno_service.actualizar_evaluaciones_examen(examen, data)
        except AlumnosError as exc: mensaje_error_validacion(request, exc)
        else: messages.success(request, "Evaluaciones guardadas correctamente.")
        return redirect("alumnos:examen_detail", alumno_id=alumno.pk, examen_id=examen.pk)
    return render(request, "alumnos/examenes/examen_evaluaciones_form.html", {"alumno": alumno, "examen": examen, "detalles": detalles, "conceptos_gup_validos": examen_alumno_service.CONCEPTOS_GUP_VALIDOS})

def _cambiar_estado(request, alumno_id, examen_id, accion, mensaje):
    alumno, examen = _obtener_examen(request, alumno_id, examen_id)
    if request.method == "POST":
        try: accion(examen)
        except AlumnosError as exc: mensaje_error_validacion(request, exc)
        else: messages.success(request, mensaje)
    return redirect("alumnos:alumno_detail", pk=alumno.pk)

@login_required
def examen_aprobar(request, alumno_id, examen_id): return _cambiar_estado(request, alumno_id, examen_id, examen_alumno_service.aprobar_examen, "Examen aprobado correctamente.")
@login_required
def examen_desaprobar(request, alumno_id, examen_id): return _cambiar_estado(request, alumno_id, examen_id, examen_alumno_service.desaprobar_examen, "Examen desaprobado correctamente.")
@login_required
def examen_anular(request, alumno_id, examen_id): return _cambiar_estado(request, alumno_id, examen_id, examen_alumno_service.anular_examen, "Examen anulado correctamente.")
