from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AsistenciaClase(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PRESENTE = "PRESENTE", "Presente"
        AUSENTE = "AUSENTE", "Ausente"
        JUSTIFICADA = "JUSTIFICADA", "Ausencia justificada"
        TARDE = "TARDE", "Llego tarde"

    sesion = models.ForeignKey(
        "clases.ClaseSesion",
        on_delete=models.PROTECT,
        related_name="asistencias",
        db_column="id_sesion",
    )
    clase_alumno = models.ForeignKey(
        "clases.ClaseAlumno",
        on_delete=models.PROTECT,
        related_name="asistencias",
        db_column="id_clase_alumno",
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    observaciones = models.TextField(null=True, blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="asistencias_registradas",
        null=True,
        blank=True,
        db_column="id_usuario_registro",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clases_asistencias"
        ordering = ["clase_alumno__alumno_escuela__alumno__apellido"]
        constraints = [
            models.UniqueConstraint(
                fields=["sesion", "clase_alumno"],
                name="uq_asistencia_sesion_alumno",
            )
        ]
        verbose_name = "Asistencia de clase"
        verbose_name_plural = "Asistencias de clases"

    def clean(self):
        if (
            self.sesion_id
            and self.clase_alumno_id
            and self.sesion.clase_id != self.clase_alumno.clase_id
        ):
            raise ValidationError(
                {"clase_alumno": "La asistencia debe pertenecer a la clase de la sesion."}
            )

    def __str__(self):
        return f"{self.clase_alumno} - {self.sesion} - {self.get_estado_display()}"
