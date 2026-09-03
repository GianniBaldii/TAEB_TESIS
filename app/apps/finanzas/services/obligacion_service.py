from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.escuelas.services.acceso_escuela_service import validar_acceso_a_escuela
from ..models import ObligacionPago
from .excepciones import FinanzasError


def calcular_fecha_atraso(fecha_vencimiento, dias_tolerancia):
    return fecha_vencimiento + timedelta(days=dias_tolerancia + 1)


def normalizar_inscripciones(alumnos_escuela):
    return list({inscripcion.pk: inscripcion for inscripcion in alumnos_escuela}.values())


def validar_inscripcion(*, escuela, inscripcion):
    if inscripcion.escuela_id != escuela.pk:
        raise FinanzasError("El alumno no pertenece a la escuela activa.")
    if not inscripcion.activo or not inscripcion.alumno.activo:
        raise FinanzasError("Solo se pueden generar cobros para alumnos con inscripción activa.")


@transaction.atomic
def crear_obligaciones(*, escuela, concepto, alumnos_escuela, monto, fecha_vencimiento, dias_tolerancia, descripcion, usuario, claves_origen=None, periodo_anio=None, periodo_mes=None):
    validar_acceso_a_escuela(usuario, escuela)
    if concepto.escuela_id != escuela.pk or not concepto.activo:
        raise FinanzasError("El concepto no está activo para la escuela.")
    monto = Decimal(monto)
    if monto <= 0:
        raise FinanzasError("El monto debe ser mayor que cero.")
    inscripciones = normalizar_inscripciones(alumnos_escuela)
    for inscripcion in inscripciones:
        validar_inscripcion(escuela=escuela, inscripcion=inscripcion)
    claves_origen = claves_origen or {}
    creadas, omitidas = [], []
    fecha_atraso = calcular_fecha_atraso(fecha_vencimiento, dias_tolerancia)
    for inscripcion in inscripciones:
        clave = claves_origen.get(inscripcion.pk)
        datos = {
            "escuela": escuela, "alumno_escuela": inscripcion,
            "concepto_financiero": concepto, "descripcion": descripcion,
            "monto_original": monto, "periodo_anio": periodo_anio,
            "periodo_mes": periodo_mes, "fecha_generacion": timezone.localdate(),
            "fecha_vencimiento": fecha_vencimiento, "fecha_atraso": fecha_atraso,
            "creado_por": usuario,
        }
        if clave:
            obligacion, creada = ObligacionPago.objects.get_or_create(
                clave_origen=clave, defaults=datos
            )
            (creadas if creada else omitidas).append(obligacion if creada else inscripcion)
        else:
            creadas.append(ObligacionPago.objects.create(**datos))
    return {"creadas": creadas, "omitidas": omitidas}
