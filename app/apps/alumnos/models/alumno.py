from django.db import models

from .cinturon import Cinturon


class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=30, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    peso_aproximado = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    altura_aproximada = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    cinturon_actual = models.ForeignKey(
        Cinturon,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="alumnos_actuales",
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"
