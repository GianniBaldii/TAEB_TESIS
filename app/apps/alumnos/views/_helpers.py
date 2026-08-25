from django.contrib import messages
from django.shortcuts import get_object_or_404
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario
from ..selectors import alumno_selectors

def mensaje_error_validacion(request, error):
    messages.error(request, str(error), extra_tags="validation_error")

def escuela_operativa(request):
    return obtener_escuela_activa_usuario(request.user)

def alumno_accesible(request, alumno_id, incluir_inactiva=False):
    inscripciones = alumno_selectors.inscripciones_visibles_para_usuario(request.user, incluir_inactivas=incluir_inactiva)
    inscripcion = get_object_or_404(inscripciones, alumno_id=alumno_id)
    return inscripcion.alumno, inscripcion

def examen_queryset(alumno):
    return alumno_selectors.examenes_del_alumno(alumno)
