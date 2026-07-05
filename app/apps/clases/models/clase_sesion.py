from django.core.exceptions import ValidationError
from django.db import models


class ClaseSesion(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = "PROGRAMADA", "Programada"
        EN_CURSO = "EN_CURSO", "En curso"
        FINALIZADA = "FINALIZADA", "Finalizada"
        CANCELADA = "CANCELADA", "Cancelada"

    clase = models.ForeignKey(
        "clases.Clase",
        on_delete=models.PROTECT,
        related_name="sesiones",
    )
    horario = models.ForeignKey(
        "clases.ClaseHorario",
        on_delete=models.PROTECT,
        related_name="sesiones",
        null=True,
        blank=True,
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    docente_a_cargo = models.ForeignKey(
        "escuelas.EscuelaDocente",
        on_delete=models.PROTECT,
        related_name="sesiones_a_cargo",
        null=True,
        blank=True,
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
    )
    es_clase_extra = models.BooleanField(default=False)
    motivo_cancelacion = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["clase", "fecha", "hora_inicio"],
                name="uq_clase_sesion_fecha_hora",
            )
        ]
        verbose_name = "Sesion de clase"
        verbose_name_plural = "Sesiones de clases"

    def clean(self):
        errores = {}
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            errores["hora_fin"] = "La hora de fin debe ser posterior a la hora de inicio."
        if self.horario_id and self.horario.clase_id != self.clase_id:
            errores["horario"] = "El horario debe pertenecer a la misma clase."
        if self.es_clase_extra and self.horario_id:
            errores["horario"] = "Una clase extra no debe tener horario recurrente."
        if self.docente_a_cargo_id:
            if self.docente_a_cargo.escuela_id != self.clase.escuela_id:
                errores["docente_a_cargo"] = (
                    "El docente a cargo debe pertenecer a la misma escuela."
                )
            if not self.docente_a_cargo.activo:
                errores["docente_a_cargo"] = (
                    "El docente a cargo debe tener una relacion activa."
                )
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f"{self.clase.nombre} - {self.fecha} {self.hora_inicio:%H:%M}"

