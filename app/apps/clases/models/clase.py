from django.core.exceptions import ValidationError
from django.db import models


class Clase(models.Model):
    escuela = models.ForeignKey(
        "escuelas.Escuela",
        on_delete=models.PROTECT,
        related_name="clases",
        db_column="id_escuela",
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    docente_responsable = models.ForeignKey(
        "escuelas.EscuelaDocente",
        on_delete=models.PROTECT,
        related_name="clases_responsables",
        null=True,
        blank=True,
        db_column="id_docente_responsable",
    )
    cupo_maximo = models.PositiveSmallIntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clases"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["escuela", "nombre"],
                name="uq_clase_escuela_nombre",
            )
        ]
        verbose_name = "Clase"
        verbose_name_plural = "Clases"

    def clean(self):
        errores = {}
        if self.cupo_maximo is not None and self.cupo_maximo < 1:
            errores["cupo_maximo"] = "El cupo maximo debe ser mayor o igual a 1."
        if self.docente_responsable_id:
            if self.docente_responsable.escuela_id != self.escuela_id:
                errores["docente_responsable"] = (
                    "El docente responsable debe pertenecer a la misma escuela."
                )
            if not self.docente_responsable.activo:
                errores["docente_responsable"] = (
                    "El docente responsable debe tener una relacion activa."
                )
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f"{self.nombre} - {self.escuela}"
