from django.db import models


class Cinturon(models.Model):
    class TipoRango(models.TextChoices):
        GUP = "GUP", "GUP"
        DAN = "DAN", "DAN"

    nombre = models.CharField(max_length=100)
    color = models.CharField(max_length=80)
    tipo_rango = models.CharField(max_length=3, choices=TipoRango.choices)
    numeracion = models.PositiveSmallIntegerField()
    orden = models.PositiveSmallIntegerField(unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo_rango", "numeracion"],
                name="cinturon_tipo_rango_numeracion_unicos",
            )
        ]
        verbose_name = "Cinturon"
        verbose_name_plural = "Cinturones"

    def __str__(self):
        return f"{self.nombre} ({self.tipo_rango} {self.numeracion})"
