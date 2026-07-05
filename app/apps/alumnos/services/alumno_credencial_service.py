import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone

from apps.alumnos.constants.seguridad_mobile import (
    BLOQUEO_LOGIN_MOBILE_MINUTOS,
    MAXIMO_INTENTOS_LOGIN_MOBILE,
)
from apps.alumnos.models import AlumnoCredencial, AlumnoEscuela
from apps.escuelas.services.acceso_escuela_service import validar_acceso_a_escuela

from .excepciones import AlumnosError


def normalizar_dni_para_username(dni):
    username = re.sub(r"\D", "", dni or "")
    if not username:
        raise AlumnosError("El DNI del alumno es obligatorio para generar credenciales.")
    if not username.isdigit():
        raise AlumnosError("El DNI debe contener solo numeros luego de normalizarse.")
    return username


def validar_acceso_gestion_credencial(*, actor, alumno):
    if actor.is_superuser:
        return True
    inscripcion = (
        AlumnoEscuela.objects.select_related("escuela")
        .filter(alumno=alumno, activo=True, escuela__activo=True)
        .first()
    )
    if not inscripcion:
        raise AlumnosError("El alumno no tiene una inscripcion activa en una escuela.")
    validar_acceso_a_escuela(actor, inscripcion.escuela)
    return True


def _validar_alumno_apto_para_credencial(alumno):
    if not alumno.activo:
        raise AlumnosError("No se pueden generar credenciales para un alumno inactivo.")
    if not AlumnoEscuela.objects.filter(
        alumno=alumno,
        activo=True,
        escuela__activo=True,
    ).exists():
        raise AlumnosError("El alumno debe tener al menos una escuela activa.")


def _validar_password(password, password_confirmacion, usuario=None):
    if password != password_confirmacion:
        raise AlumnosError("Las contrasenas ingresadas no coinciden.")
    try:
        validate_password(password, user=usuario)
    except Exception as exc:
        raise AlumnosError(exc) from exc


def _obtener_credencial_existente_usuario(username):
    usuario = get_user_model().objects.filter(username=username).first()
    if not usuario:
        return None, None
    credencial = getattr(usuario, "credencial_alumno", None)
    return usuario, credencial


@transaction.atomic
def crear_credencial_mobile_para_alumno(
    *,
    alumno,
    password,
    password_confirmacion,
    actor,
):
    validar_acceso_gestion_credencial(actor=actor, alumno=alumno)
    _validar_alumno_apto_para_credencial(alumno)
    if hasattr(alumno, "credencial_mobile"):
        raise AlumnosError("El alumno ya posee credenciales mobile.")

    username = normalizar_dni_para_username(alumno.dni)
    usuario_existente, credencial_existente = _obtener_credencial_existente_usuario(username)
    if usuario_existente and not credencial_existente:
        raise AlumnosError("Ya existe un usuario con el DNI del alumno.")
    if credencial_existente and credencial_existente.alumno_id != alumno.id:
        raise AlumnosError("Ya existe una credencial mobile para ese DNI.")

    User = get_user_model()
    usuario = User(
        username=username,
        first_name=alumno.nombre,
        last_name=alumno.apellido,
        email=alumno.email or "",
        is_active=True,
    )
    _validar_password(password, password_confirmacion, usuario=usuario)
    usuario.set_password(password)
    usuario.save()

    return AlumnoCredencial.objects.create(
        alumno=alumno,
        usuario=usuario,
        acceso_habilitado=True,
        debe_cambiar_password=True,
    )


@transaction.atomic
def resetear_password_credencial_mobile(
    *,
    credencial,
    password,
    password_confirmacion,
    actor,
):
    validar_acceso_gestion_credencial(actor=actor, alumno=credencial.alumno)
    _validar_password(password, password_confirmacion, usuario=credencial.usuario)
    credencial.usuario.set_password(password)
    credencial.usuario.save(update_fields=["password"])
    credencial.debe_cambiar_password = True
    credencial.fecha_ultimo_reset_password = timezone.now()
    credencial.save(
        update_fields=[
            "debe_cambiar_password",
            "fecha_ultimo_reset_password",
            "fecha_modificacion",
        ]
    )
    revocar_sesiones_mobile_alumno(usuario=credencial.usuario)
    return credencial


@transaction.atomic
def bloquear_acceso_mobile(*, credencial, actor, motivo=None):
    validar_acceso_gestion_credencial(actor=actor, alumno=credencial.alumno)
    credencial.acceso_habilitado = False
    credencial.save(update_fields=["acceso_habilitado", "fecha_modificacion"])
    revocar_sesiones_mobile_alumno(usuario=credencial.usuario)
    return credencial


@transaction.atomic
def reactivar_acceso_mobile(*, credencial, actor):
    validar_acceso_gestion_credencial(actor=actor, alumno=credencial.alumno)
    credencial.acceso_habilitado = True
    credencial.bloqueado_hasta = None
    credencial.intentos_fallidos = 0
    credencial.save(
        update_fields=[
            "acceso_habilitado",
            "bloqueado_hasta",
            "intentos_fallidos",
            "fecha_modificacion",
        ]
    )
    return credencial


def revocar_sesiones_mobile_alumno(*, usuario):
    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
    except Exception:
        return 0

    revocadas = 0
    for token in OutstandingToken.objects.filter(user=usuario):
        try:
            token.blacklist()
            revocadas += 1
        except Exception:
            continue
    return revocadas


def credencial_tiene_bloqueo_temporal_activo(credencial):
    return bool(credencial.bloqueado_hasta and credencial.bloqueado_hasta > timezone.now())


def registrar_login_fallido(credencial):
    credencial.intentos_fallidos += 1
    update_fields = ["intentos_fallidos", "fecha_modificacion"]
    if credencial.intentos_fallidos >= MAXIMO_INTENTOS_LOGIN_MOBILE:
        credencial.bloqueado_hasta = timezone.now() + timezone.timedelta(
            minutes=BLOQUEO_LOGIN_MOBILE_MINUTOS
        )
        update_fields.append("bloqueado_hasta")
    credencial.save(update_fields=update_fields)
    return credencial


def registrar_login_exitoso(credencial):
    credencial.ultimo_login_mobile = timezone.now()
    credencial.intentos_fallidos = 0
    credencial.bloqueado_hasta = None
    credencial.save(
        update_fields=[
            "ultimo_login_mobile",
            "intentos_fallidos",
            "bloqueado_hasta",
            "fecha_modificacion",
        ]
    )
    return credencial
