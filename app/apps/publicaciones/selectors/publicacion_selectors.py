from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario

from ..models import Publicacion


def publicaciones_visibles_para_usuario(usuario):
    publicaciones = Publicacion.objects.select_related("escuela", "creado_por")
    if usuario.is_superuser:
        return publicaciones
    return publicaciones.filter(escuela=obtener_escuela_activa_usuario(usuario))
