from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.escuelas.models import EscuelaDocente
from apps.escuelas.services.excepciones import EscuelasError
from apps.usuarios.models import Docente


@transaction.atomic
def crear_docente_con_usuario_y_escuela(datos_usuario, datos_docente, escuela, rol):
    if not escuela.activo:
        raise EscuelasError("No se puede asignar un docente a una escuela inactiva.")
    usuario = get_user_model().objects.create_user(**datos_usuario)
    docente = Docente.objects.create(usuario=usuario, **datos_docente)
    EscuelaDocente.objects.create(escuela=escuela, docente=docente, rol=rol)
    return docente


@transaction.atomic
def desactivar_docente(docente):
    docente.activo = False
    docente.save(update_fields=["activo", "fecha_modificacion"])
    docente.usuario.is_active = False
    docente.usuario.save(update_fields=["is_active"])
    docente.escuelas.filter(activo=True).update(activo=False, fecha_baja=timezone.localdate())
    return docente


def reactivar_docente(docente):
    docente.activo = True
    docente.save(update_fields=["activo", "fecha_modificacion"])
    docente.usuario.is_active = True
    docente.usuario.save(update_fields=["is_active"])
    return docente


def resetear_password_docente(docente, nueva_password):
    docente.usuario.set_password(nueva_password)
    docente.usuario.save(update_fields=["password"])
    return docente


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
