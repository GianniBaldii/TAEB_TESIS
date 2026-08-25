from datetime import date, timedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario
from ..models import ClaseHorario, ClaseSesion
from ..selectors import clase_selectors
from ..services import clase_service

def mensaje_error_validacion(request, error): messages.error(request, str(error), extra_tags="validation_error")
def escuela_operativa(request): return obtener_escuela_activa_usuario(request.user)
def escuelas_visibles(request): return clase_selectors.escuelas_visibles_para_usuario(request.user)
def clase_queryset(request): return clase_selectors.clases_visibles_para_usuario(request.user)
def clase_accesible(request, clase_id):
    clase = get_object_or_404(clase_queryset(request), pk=clase_id); clase_service.validar_acceso_clase(request.user, clase); return clase
def horario_accesible(request, horario_id):
    horario = get_object_or_404(ClaseHorario.objects.select_related("clase", "clase__escuela"), pk=horario_id); clase_service.validar_acceso_clase(request.user, horario.clase); return horario
def sesion_accesible(request, sesion_id):
    sesion = get_object_or_404(ClaseSesion.objects.select_related("clase", "clase__escuela", "docente_a_cargo", "docente_a_cargo__docente__usuario"), pk=sesion_id); clase_service.validar_acceso_clase(request.user, sesion.clase); return sesion
def rango_calendario(request):
    fecha_base = parse_date(request.GET.get("fecha", "")) or date.today(); vista = request.GET.get("vista", "semana")
    if vista == "dia": return fecha_base, fecha_base, "dia"
    inicio = fecha_base - timedelta(days=fecha_base.weekday()); return inicio, inicio + timedelta(days=6), "semana"
