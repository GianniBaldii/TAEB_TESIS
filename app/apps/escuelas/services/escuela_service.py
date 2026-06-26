from apps.escuelas.models import Escuela

from .excepciones import EscuelasError


ESCUELA_CAMPOS_EDITABLES = {
    "nombre", "nombre_comercial", "razon_social", "cuit", "email", "telefono",
    "direccion", "ciudad", "provincia",
}


def validar_usuario_superadmin(usuario):
    if not usuario.is_authenticated or not usuario.is_superuser:
        raise EscuelasError("Esta acción requiere permisos de superadministrador.")


def _filtrar_datos(data):
    return {campo: valor for campo, valor in data.items() if campo in ESCUELA_CAMPOS_EDITABLES}


def crear_escuela(data):
    return Escuela.objects.create(**_filtrar_datos(data))


def actualizar_escuela(escuela, data):
    if not escuela.activo:
        raise EscuelasError("No se puede editar una escuela inactiva.")
    datos = _filtrar_datos(data)
    for campo, valor in datos.items():
        setattr(escuela, campo, valor)
    escuela.save(update_fields=[*datos.keys(), "fecha_modificacion"])
    return escuela


def activar_escuela(escuela):
    escuela.activo = True
    escuela.save(update_fields=["activo", "fecha_modificacion"])
    return escuela


def desactivar_escuela(escuela):
    escuela.activo = False
    escuela.save(update_fields=["activo", "fecha_modificacion"])
    return escuela
