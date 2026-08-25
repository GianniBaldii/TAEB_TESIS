from django.utils import timezone
from ..models import EscuelaDocente
from .excepciones import EscuelasError

def vincular_docente_a_escuela(docente, escuela, rol):
    if not escuela.activo:
        raise EscuelasError("No se puede asignar una escuela inactiva.")
    relacion, creada = EscuelaDocente.objects.get_or_create(docente=docente, escuela=escuela, defaults={"rol": rol, "activo": True})
    if not creada:
        if relacion.activo:
            raise EscuelasError("El docente ya está asociado a esta escuela.")
        relacion.activo, relacion.rol, relacion.fecha_baja = True, rol, None
        relacion.save(update_fields=["activo", "rol", "fecha_baja"])
    return relacion

def cambiar_estado_relacion(relacion, activar):
    if activar and (not relacion.docente.activo or not relacion.escuela.activo):
        raise EscuelasError("El docente y la escuela deben estar activos.")
    relacion.activo = activar
    relacion.fecha_baja = None if activar else timezone.localdate()
    relacion.save(update_fields=["activo", "fecha_baja"])
    return relacion
