from django.conf import settings
from django.db import models


class Docente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="perfil_docente",
        db_column="id_usuario",
    )
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=30, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "usuarios_docentes"
        ordering = ["usuario__last_name", "usuario__first_name", "usuario__username"]
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username
