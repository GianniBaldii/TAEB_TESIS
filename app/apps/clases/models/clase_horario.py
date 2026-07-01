from django.core.exceptions import ValidationError
from django.db import models


class ClaseHorario(models.Model):
    class DiaSemana(models.IntegerChoices):
        LUNES = 0, "Lunes"
        MARTES = 1, "Martes"
        MIERCOLES = 2, "Miercoles"
        JUEVES = 3, "Jueves"
        VIERNES = 4, "Viernes"
        SABADO = 5, "Sabado"
        DOMINGO = 6, "Domingo"

    clase = models.ForeignKey(
        "clases.Clase",
        on_delete=models.CASCADE,
        related_name="horarios",
    )
    dia_semana = models.PositiveSmallIntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_desde = models.DateField(null=True, blank=True)
    fecha_hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["dia_semana", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["clase", "dia_semana", "hora_inicio"],
                name="uq_clase_horario",
            )
        ]
        verbose_name = "Horario de clase"
        verbose_name_plural = "Horarios de clases"

    def clean(self):
        errores = {}
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            errores["hora_fin"] = "La hora de fin debe ser posterior a la hora de inicio."
        if self.fecha_desde and self.fecha_hasta and self.fecha_hasta < self.fecha_desde:
            errores["fecha_hasta"] = "La fecha hasta no puede ser anterior a la fecha desde."
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return (
            f"{self.clase} - {self.get_dia_semana_display()} "
            f"{self.hora_inicio:%H:%M}"
        )

