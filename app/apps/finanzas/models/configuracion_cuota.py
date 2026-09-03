from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class ConfiguracionCuota(models.Model):
    escuela = models.OneToOneField("escuelas.Escuela", on_delete=models.PROTECT, related_name="configuracion_cuota", db_column="id_escuela")
    monto_actual = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    dia_vencimiento = models.PositiveSmallIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(28)])
    dias_tolerancia = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "finanzas_configuraciones_cuota"

    def __str__(self):
        return f"Cuota {self.escuela}: ${self.monto_actual}"
