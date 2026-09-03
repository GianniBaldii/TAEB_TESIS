from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class Pago(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "EFECTIVO", "Efectivo"
        TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"

    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        CONFIRMADO = "CONFIRMADO", "Confirmado"
        ANULADO = "ANULADO", "Anulado"

    escuela = models.ForeignKey("escuelas.Escuela", on_delete=models.PROTECT, related_name="pagos", db_column="id_escuela")
    alumno_escuela = models.ForeignKey("alumnos.AlumnoEscuela", on_delete=models.PROTECT, related_name="pagos", db_column="id_alumno_escuela")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    metodo_pago = models.CharField(max_length=20, choices=Metodo.choices)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.CONFIRMADO)
    fecha_pago = models.DateField()
    referencia = models.CharField(max_length=150, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pagos_registrados", db_column="id_usuario_registro")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "finanzas_pagos"
        ordering = ["-fecha_pago", "-pk"]

    def __str__(self):
        return f"Pago #{self.pk} - ${self.monto_total}"

    def clean(self):
        if self.alumno_escuela_id and self.escuela_id and self.alumno_escuela.escuela_id != self.escuela_id:
            raise ValidationError({"alumno_escuela": "La inscripción debe pertenecer a la misma escuela."})
