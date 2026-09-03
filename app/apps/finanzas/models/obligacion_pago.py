from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class ObligacionPago(models.Model):
    class EstadoOperativo(models.TextChoices):
        ACTIVA = "ACTIVA", "Activa"
        ANULADA = "ANULADA", "Anulada"

    escuela = models.ForeignKey("escuelas.Escuela", on_delete=models.PROTECT, related_name="obligaciones_pago", db_column="id_escuela")
    alumno_escuela = models.ForeignKey("alumnos.AlumnoEscuela", on_delete=models.PROTECT, related_name="obligaciones_pago", db_column="id_alumno_escuela")
    concepto_financiero = models.ForeignKey("finanzas.ConceptoFinanciero", on_delete=models.PROTECT, related_name="obligaciones", db_column="id_concepto_financiero")
    descripcion = models.CharField(max_length=255)
    monto_original = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    periodo_anio = models.PositiveSmallIntegerField(null=True, blank=True)
    periodo_mes = models.PositiveSmallIntegerField(null=True, blank=True)
    fecha_generacion = models.DateField()
    fecha_vencimiento = models.DateField()
    fecha_atraso = models.DateField()
    clave_origen = models.CharField(max_length=100, null=True, blank=True, unique=True)
    estado_operativo = models.CharField(max_length=10, choices=EstadoOperativo.choices, default=EstadoOperativo.ACTIVA)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="obligaciones_creadas", db_column="id_usuario_creacion")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "finanzas_obligaciones"
        ordering = ["-fecha_generacion", "-pk"]
        indexes = [models.Index(fields=["escuela", "periodo_anio", "periodo_mes"], name="idx_fin_oblig_periodo")]

    def __str__(self):
        return f"{self.descripcion} - {self.alumno_escuela.alumno}"

    def clean(self):
        if self.alumno_escuela_id and self.escuela_id and self.alumno_escuela.escuela_id != self.escuela_id:
            raise ValidationError({"alumno_escuela": "La inscripción debe pertenecer a la misma escuela."})
