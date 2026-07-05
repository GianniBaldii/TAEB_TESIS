from django.core.exceptions import ValidationError

from apps.escuelas.services.acceso_escuela_service import validar_acceso_a_escuela

from ..models import Clase
from .excepciones import ClasesError


CLASE_CAMPOS_EDITABLES = {
    "escuela",
    "nombre",
    "descripcion",
    "docente_responsable",
    "cupo_maximo",
    "activo",
}


def _normalizar_data(data):
    return {campo: valor for campo, valor in data.items() if campo in CLASE_CAMPOS_EDITABLES}


def _validar_clase(clase):
    try:
        clase.full_clean()
    except ValidationError as exc:
        raise ClasesError(exc) from exc


def crear_clase(escuela, data, docente_responsable=None):
    datos = _normalizar_data(data)
    datos["escuela"] = escuela
    if docente_responsable is not None:
        datos["docente_responsable"] = docente_responsable
    clase = Clase(**datos)
    _validar_clase(clase)
    clase.save()
    return clase


def actualizar_clase(clase, data):
    for campo, valor in _normalizar_data(data).items():
        if campo != "escuela":
            setattr(clase, campo, valor)
    _validar_clase(clase)
    clase.save()
    return clase


def activar_clase(clase):
    clase.activo = True
    clase.save(update_fields=["activo", "fecha_modificacion"])
    return clase


def desactivar_clase(clase):
    clase.activo = False
    clase.save(update_fields=["activo", "fecha_modificacion"])
    return clase


def validar_acceso_clase(usuario, clase):
    validar_acceso_a_escuela(usuario, clase.escuela)
    return True

