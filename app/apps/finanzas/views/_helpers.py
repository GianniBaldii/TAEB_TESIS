from django.contrib import messages
from django.shortcuts import get_object_or_404

from apps.escuelas.models import Escuela
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario
from ..models import ObligacionPago
from ..selectors.finanzas_selectors import obligaciones_con_saldo


def escuela_operativa(request):
    if request.user.is_superuser:
        return get_object_or_404(Escuela.objects.filter(activo=True).order_by("pk"))
    return obtener_escuela_activa_usuario(request.user)


def obligacion_accesible(request, pk):
    escuela = escuela_operativa(request)
    return get_object_or_404(obligaciones_con_saldo(ObligacionPago.objects.filter(escuela=escuela)), pk=pk)


def informar_error(request, error):
    messages.error(request, str(error), extra_tags="validation_error")
