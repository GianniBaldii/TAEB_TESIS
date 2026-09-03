from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from apps.escuelas.services.acceso_escuela_service import validar_acceso_a_escuela
from ..models import ObligacionPago, Pago, PagoAplicacion
from .excepciones import FinanzasError


def saldo_obligacion(obligacion):
    pagado = obligacion.aplicaciones_pago.filter(pago__estado=Pago.Estado.CONFIRMADO).aggregate(total=Sum("monto_aplicado"))["total"] or Decimal("0")
    return obligacion.monto_original - pagado


@transaction.atomic
def registrar_pago(*, obligacion, monto, metodo, fecha_pago, referencia, observaciones, usuario):
    obligacion = ObligacionPago.objects.select_for_update().select_related("escuela", "alumno_escuela").get(pk=obligacion.pk)
    validar_acceso_a_escuela(usuario, obligacion.escuela)
    if obligacion.estado_operativo != ObligacionPago.EstadoOperativo.ACTIVA:
        raise FinanzasError("No se puede pagar una obligación anulada.")
    if metodo not in Pago.Metodo.values:
        raise FinanzasError("El método de pago no es válido.")
    monto = Decimal(monto)
    saldo = saldo_obligacion(obligacion)
    if monto <= 0 or monto > saldo:
        raise FinanzasError("El monto debe ser mayor que cero y no superar el saldo.")
    pago = Pago.objects.create(
        escuela=obligacion.escuela, alumno_escuela=obligacion.alumno_escuela,
        monto_total=monto, metodo_pago=metodo, estado=Pago.Estado.CONFIRMADO,
        fecha_pago=fecha_pago, referencia=referencia, observaciones=observaciones,
        registrado_por=usuario,
    )
    PagoAplicacion.objects.create(pago=pago, obligacion_pago=obligacion, monto_aplicado=monto)
    return pago
