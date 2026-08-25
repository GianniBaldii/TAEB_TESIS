from apps.escuelas.models import Escuela
from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario

from ..models import Clase


def escuelas_visibles_para_usuario(usuario):
    escuelas = Escuela.objects.filter(activo=True)
    if usuario.is_superuser:
        return escuelas
    return escuelas.filter(pk=obtener_escuela_activa_usuario(usuario).pk)


def clases_visibles_para_usuario(usuario):
    clases = Clase.objects.select_related(
        "escuela",
        "docente_responsable",
        "docente_responsable__docente__usuario",
    )
    if usuario.is_superuser:
        return clases
    return clases.filter(escuela=obtener_escuela_activa_usuario(usuario))
