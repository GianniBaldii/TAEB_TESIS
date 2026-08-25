from django.db import models


class AlumnoEscuela(models.Model):
    alumno = models.ForeignKey(
        "Alumno", on_delete=models.PROTECT, related_name="inscripciones_escuela",
        db_column="id_alumno",
    )
    escuela = models.ForeignKey(
        "escuelas.Escuela", on_delete=models.PROTECT, related_name="alumnos_inscriptos",
        db_column="id_escuela",
    )
    activo = models.BooleanField(default=True)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumnos_escuelas"
        ordering = ["-activo", "alumno__apellido", "alumno__nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["alumno", "escuela"], name="uq_alumno_escuela"
            )
        ]
        verbose_name = "Inscripción de alumno"
        verbose_name_plural = "Inscripciones de alumnos"

    def __str__(self):
        return f"{self.alumno} - {self.escuela}"
