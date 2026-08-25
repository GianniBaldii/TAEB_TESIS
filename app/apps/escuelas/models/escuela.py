from django.db import models


class Escuela(models.Model):
    nombre = models.CharField(max_length=150)
    nombre_comercial = models.CharField(max_length=150, null=True, blank=True)
    razon_social = models.CharField(max_length=150, null=True, blank=True)
    cuit = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telefono = models.CharField(max_length=30, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    provincia = models.CharField(max_length=100, null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "escuelas"
        ordering = ["nombre"]
        verbose_name = "Escuela"
        verbose_name_plural = "Escuelas"

    def __str__(self):
        return self.nombre_comercial or self.nombre
