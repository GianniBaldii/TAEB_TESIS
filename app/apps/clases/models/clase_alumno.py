from django.core.exceptions import ValidationError
from django.db import models


class ClaseAlumno(models.Model):
    clase = models.ForeignKey(
        "clases.Clase",
        on_delete=models.PROTECT,
        related_name="inscripciones_alumnos",
    )
    alumno_escuela = models.ForeignKey(
        "alumnos.AlumnoEscuela",
        on_delete=models.PROTECT,
        related_name="clases_inscriptas",
    )
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activo", "alumno_escuela__alumno__apellido"]
        constraints = [
            models.UniqueConstraint(
                fields=["clase", "alumno_escuela"],
                name="uq_clase_alumno",
            )
        ]
        verbose_name = "Inscripcion a clase"
        verbose_name_plural = "Inscripciones a clases"

    def clean(self):
        if (
            self.clase_id
            and self.alumno_escuela_id
            and self.clase.escuela_id != self.alumno_escuela.escuela_id
        ):
            raise ValidationError(
                {"alumno_escuela": "El alumno debe pertenecer a la escuela de la clase."}
            )

    def __str__(self):
        return f"{self.alumno_escuela.alumno} - {self.clase}"

