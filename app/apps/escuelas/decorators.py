from functools import wraps

from django.core.exceptions import PermissionDenied

from .services.acceso_escuela_service import obtener_escuela_activa_usuario
from .services.excepciones import EscuelaActivaNoEncontradaError


def requerir_superadmin(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped_view


def requerir_escuela_activa(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        try:
            request.escuela_activa = obtener_escuela_activa_usuario(request.user)
        except EscuelaActivaNoEncontradaError as exc:
            raise PermissionDenied(str(exc)) from exc
        return view_func(request, *args, **kwargs)

    return wrapped_view
