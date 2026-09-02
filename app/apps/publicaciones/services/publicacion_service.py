from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.escuelas.services.acceso_escuela_service import validar_acceso_a_escuela

from ..models import Publicacion
from .excepciones import PublicacionesError


CAMPOS_EDITABLES = {
    "titulo",
    "descripcion",
    "tipo_publicacion",
    "tematica",
    "fecha_hora_inicio",
    "fecha_hora_fin",
    "ubicacion",
    "cupo_maximo",
}


def _datos_editables(data):
    return {campo: valor for campo, valor in data.items() if campo in CAMPOS_EDITABLES}


def _validar(publicacion):
    try:
        publicacion.full_clean()
    except ValidationError as exc:
        raise PublicacionesError(exc) from exc


def _validar_operable(publicacion, usuario):
    validar_acceso_a_escuela(usuario, publicacion.escuela)
    if not publicacion.activo:
        raise PublicacionesError("La publicación está desactivada y no admite nuevas operaciones.")


def crear_publicacion(*, escuela, usuario, data):
    validar_acceso_a_escuela(usuario, escuela)
    publicacion = Publicacion(
        escuela=escuela,
        creado_por=usuario,
        estado=Publicacion.Estado.BORRADOR,
        activo=True,
        **_datos_editables(data),
    )
    _validar(publicacion)
    publicacion.save()
    return publicacion


def actualizar_publicacion(publicacion, *, usuario, data):
    _validar_operable(publicacion, usuario)
    if publicacion.estado != Publicacion.Estado.BORRADOR:
        raise PublicacionesError("Solo se pueden editar publicaciones en borrador.")
    for campo, valor in _datos_editables(data).items():
        setattr(publicacion, campo, valor)
    _validar(publicacion)
    publicacion.save()
    return publicacion


def publicar_publicacion(publicacion, *, usuario):
    _validar_operable(publicacion, usuario)
    if publicacion.estado != Publicacion.Estado.BORRADOR:
        raise PublicacionesError("Solo se puede publicar una publicación en borrador.")
    publicacion.estado = Publicacion.Estado.PUBLICADO
    if publicacion.fecha_publicacion is None:
        publicacion.fecha_publicacion = timezone.now()
    _validar(publicacion)
    publicacion.save(update_fields=["estado", "fecha_publicacion", "fecha_modificacion"])
    return publicacion


def cancelar_publicacion(publicacion, *, usuario):
    _validar_operable(publicacion, usuario)
    if publicacion.tipo_publicacion != Publicacion.Tipo.EVENTO:
        raise PublicacionesError("Solo los eventos pueden cancelarse.")
    if publicacion.estado != Publicacion.Estado.PUBLICADO:
        raise PublicacionesError("Solo se puede cancelar un evento publicado.")
    publicacion.estado = Publicacion.Estado.CANCELADO
    _validar(publicacion)
    publicacion.save(update_fields=["estado", "fecha_modificacion"])
    return publicacion


def finalizar_publicacion(publicacion, *, usuario):
    _validar_operable(publicacion, usuario)
    if publicacion.tipo_publicacion != Publicacion.Tipo.EVENTO:
        raise PublicacionesError("Solo los eventos pueden finalizarse.")
    if publicacion.estado != Publicacion.Estado.PUBLICADO:
        raise PublicacionesError("Solo se puede finalizar un evento publicado.")
    publicacion.estado = Publicacion.Estado.FINALIZADO
    _validar(publicacion)
    publicacion.save(update_fields=["estado", "fecha_modificacion"])
    return publicacion


def desactivar_publicacion(publicacion, *, usuario):
    _validar_operable(publicacion, usuario)
    publicacion.activo = False
    publicacion.save(update_fields=["activo", "fecha_modificacion"])
    return publicacion
