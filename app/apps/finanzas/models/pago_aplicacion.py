from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class PagoAplicacion(models.Model):
    pago = models.ForeignKey("finanzas.Pago", on_delete=models.PROTECT, related_name="aplicaciones", db_column="id_pago")
    obligacion_pago = models.ForeignKey("finanzas.ObligacionPago", on_delete=models.PROTECT, related_name="aplicaciones_pago", db_column="id_obligacion_pago")
    monto_aplicado = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])

    class Meta:
        db_table = "finanzas_pagos_aplicaciones"
        constraints = [models.UniqueConstraint(fields=["pago", "obligacion_pago"], name="uq_finanzas_pago_obligacion")]

    def __str__(self):
        return f"{self.pago} -> {self.obligacion_pago}"

    def clean(self):
        if self.pago_id and self.obligacion_pago_id:
            if self.pago.escuela_id != self.obligacion_pago.escuela_id or self.pago.alumno_escuela_id != self.obligacion_pago.alumno_escuela_id:
                raise ValidationError("El pago y la obligación deben pertenecer a la misma escuela y alumno.")
