from apps.escuelas.models import EscuelaDocente
from apps.usuarios.models import Docente

from .excepciones import EscuelaActivaNoEncontradaError, EscuelasError


def obtener_docente_desde_usuario(usuario):
    if not usuario.is_authenticated or usuario.is_superuser:
        return None
    try:
        return usuario.perfil_docente
    except Docente.DoesNotExist:
        return None


def obtener_escuela_activa_usuario(usuario):
    if usuario.is_superuser:
        return None
    relacion = (
        EscuelaDocente.objects.select_related("escuela", "docente")
        .filter(
            docente__usuario=usuario,
            docente__activo=True,
            escuela__activo=True,
            activo=True,
        )
        # TODO: reemplazar esta selección temporal por un selector de escuela activa.
        .order_by("fecha_alta", "pk")
        .first()
    )
    if not relacion:
        raise EscuelaActivaNoEncontradaError(
            "No tenés una escuela activa asignada para operar."
        )
    return relacion.escuela


def usuario_tiene_acceso_a_escuela(usuario, escuela):
    if not usuario.is_authenticated:
        return False
    if usuario.is_superuser:
        return True
    return EscuelaDocente.objects.filter(
        docente__usuario=usuario,
        docente__activo=True,
        escuela=escuela,
        escuela__activo=True,
        activo=True,
    ).exists()


def validar_acceso_a_escuela(usuario, escuela):
    if not usuario_tiene_acceso_a_escuela(usuario, escuela):
        raise EscuelasError("No tenés permisos para operar en esta escuela.")
    return True
