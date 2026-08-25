from django.db import models

from .alumno import Alumno
from .cinturon import Cinturon
from .examen import Examen


class AlumnoCinturonHistorial(models.Model):
    alumno = models.ForeignKey(
        Alumno, on_delete=models.PROTECT, related_name="historial_cinturones",
        db_column="id_alumno",
    )
    cinturon = models.ForeignKey(
        Cinturon, on_delete=models.PROTECT, related_name="historial_alumnos",
        db_column="id_cinturon",
    )
    examen = models.OneToOneField(
        Examen,
        on_delete=models.PROTECT,
        related_name="historial_cinturon",
        null=True,
        blank=True,
        db_column="id_examen",
    )
    fecha_obtencion = models.DateField()
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumnos_cinturones_historial"
        ordering = ["fecha_obtencion", "cinturon__orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["alumno", "cinturon"],
                name="historial_alumno_cinturon_unicos",
            )
        ]
        verbose_name = "Historial de cinturon"
        verbose_name_plural = "Historiales de cinturones"

    def __str__(self):
        return f"{self.alumno} - {self.cinturon}"
