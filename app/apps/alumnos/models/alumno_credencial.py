from django.conf import settings
from django.db import models


class AlumnoCredencial(models.Model):
    alumno = models.OneToOneField(
        "alumnos.Alumno",
        on_delete=models.PROTECT,
        related_name="credencial_mobile",
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="credencial_alumno",
    )
    acceso_habilitado = models.BooleanField(
        default=True,
        help_text="Indica si el alumno puede iniciar sesion en la aplicacion mobile.",
    )
    debe_cambiar_password = models.BooleanField(
        default=True,
        help_text=(
            "Indica que la contrasena inicial fue creada por un docente o "
            "superadmin y deberia ser modificada por el alumno cuando exista "
            "esa funcionalidad."
        ),
    )
    ultimo_login_mobile = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    fecha_ultimo_reset_password = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Credencial mobile de alumno"
        verbose_name_plural = "Credenciales mobile de alumnos"

    def __str__(self):
        return f"{self.alumno} - {self.usuario.username}"
