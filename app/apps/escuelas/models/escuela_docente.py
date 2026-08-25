from django.db import models


class EscuelaDocente(models.Model):
    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        DOCENTE = "DOCENTE", "Docente"
        COORDINADOR = "COORDINADOR", "Coordinador"

    escuela = models.ForeignKey(
        "escuelas.Escuela", on_delete=models.PROTECT, related_name="docentes",
        db_column="id_escuela",
    )
    docente = models.ForeignKey(
        "usuarios.Docente", on_delete=models.PROTECT, related_name="escuelas",
        db_column="id_docente",
    )
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.DOCENTE)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "escuelas_docentes"
        ordering = ["fecha_alta", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["escuela", "docente"], name="uq_escuela_docente"
            )
        ]
        verbose_name = "Asignación de docente"
        verbose_name_plural = "Asignaciones de docentes"

    def __str__(self):
        return f"{self.docente} - {self.escuela}"
