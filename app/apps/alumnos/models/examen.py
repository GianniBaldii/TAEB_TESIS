from django.db import models

from .alumno import Alumno
from .cinturon import Cinturon
from .examen_template import ExamenTemplate, ExamenTemplateItem


class Examen(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        DESAPROBADO = "DESAPROBADO", "Desaprobado"
        AUSENTE = "AUSENTE", "Ausente"
        ANULADO = "ANULADO", "Anulado"

    alumno = models.ForeignKey(
        Alumno, on_delete=models.PROTECT, related_name="examenes",
        db_column="id_alumno",
    )
    examen_template = models.ForeignKey(
        ExamenTemplate, on_delete=models.PROTECT, related_name="examenes",
        db_column="id_plantilla",
    )
    cinturon_origen = models.ForeignKey(
        Cinturon, on_delete=models.PROTECT, related_name="examenes_origen",
        db_column="id_cinturon_origen",
    )
    cinturon_destino = models.ForeignKey(
        Cinturon, on_delete=models.PROTECT, related_name="examenes_destino",
        db_column="id_cinturon_destino",
    )
    fecha_examen = models.DateField()
    lugar = models.CharField(max_length=150, null=True, blank=True)
    es_historico = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.PENDIENTE
    )
    nota_final = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    resultado_final = models.CharField(max_length=20, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumnos_examenes"
        ordering = ["-fecha_examen", "-fecha_creacion"]
        verbose_name = "Examen"
        verbose_name_plural = "Examenes"

    def __str__(self):
        return f"{self.alumno} - {self.cinturon_destino} ({self.fecha_examen})"


class ExamenDetalle(models.Model):
    examen = models.ForeignKey(
        Examen, on_delete=models.CASCADE, related_name="detalles",
        db_column="id_examen",
    )
    template_item = models.ForeignKey(
        ExamenTemplateItem, on_delete=models.PROTECT, related_name="detalles_examen",
        db_column="id_plantilla_item",
    )
    nota_numerica = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    concepto = models.CharField(max_length=50, null=True, blank=True)
    valor_texto = models.TextField(null=True, blank=True)
    aprobado = models.BooleanField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "alumnos_examenes_detalles"
        ordering = ["template_item__seccion__orden", "template_item__orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["examen", "template_item"],
                name="detalle_examen_template_item_unicos",
            )
        ]
        verbose_name = "Detalle de examen"
        verbose_name_plural = "Detalles de examen"

    def __str__(self):
        return f"{self.examen} - {self.template_item}"
