from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Publicacion(models.Model):
    class Tipo(models.TextChoices):
        ANUNCIO = "ANUNCIO", "Anuncio"
        EVENTO = "EVENTO", "Evento"

    class Tematica(models.TextChoices):
        NOTICIAS = "NOTICIAS", "Noticias"
        BENEFICIOS = "BENEFICIOS", "Beneficios"
        EXAMENES = "EXAMENES", "Exámenes"
        TORNEOS = "TORNEOS", "Torneos"

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        PUBLICADO = "PUBLICADO", "Publicado"
        CANCELADO = "CANCELADO", "Cancelado"
        FINALIZADO = "FINALIZADO", "Finalizado"

    escuela = models.ForeignKey(
        "escuelas.Escuela",
        on_delete=models.PROTECT,
        related_name="publicaciones",
        db_column="id_escuela",
    )
    titulo = models.CharField(max_length=180)
    descripcion = models.TextField()
    tipo_publicacion = models.CharField(max_length=10, choices=Tipo.choices)
    tematica = models.CharField(max_length=12, choices=Tematica.choices)
    fecha_hora_inicio = models.DateTimeField(null=True, blank=True)
    fecha_hora_fin = models.DateTimeField(null=True, blank=True)
    ubicacion = models.CharField(max_length=255, null=True, blank=True)
    cupo_maximo = models.PositiveIntegerField(null=True, blank=True)
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="publicaciones_creadas",
        db_column="id_creado_por",
    )
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "publicaciones"
        ordering = ["-fecha_creacion"]
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"

    def clean(self):
        errores = {}
        if self.tipo_publicacion == self.Tipo.EVENTO and not self.fecha_hora_inicio:
            errores["fecha_hora_inicio"] = "La fecha y hora de inicio son obligatorias para un evento."
        if self.fecha_hora_fin and not self.fecha_hora_inicio:
            errores["fecha_hora_fin"] = "Para indicar una finalización primero debe indicar el inicio."
        elif (
            self.fecha_hora_inicio
            and self.fecha_hora_fin
            and self.fecha_hora_fin <= self.fecha_hora_inicio
        ):
            errores["fecha_hora_fin"] = "La finalización debe ser posterior al inicio."
        if self.cupo_maximo is not None and self.cupo_maximo < 1:
            errores["cupo_maximo"] = "El cupo máximo debe ser mayor o igual a 1."
        if self.tipo_publicacion == self.Tipo.ANUNCIO:
            if self.ubicacion:
                errores["ubicacion"] = "La ubicación solo corresponde a publicaciones de tipo evento."
            if self.cupo_maximo is not None:
                errores["cupo_maximo"] = "El cupo máximo solo corresponde a publicaciones de tipo evento."
        if self.tipo_publicacion == self.Tipo.ANUNCIO and self.estado in {
            self.Estado.CANCELADO,
            self.Estado.FINALIZADO,
        }:
            errores["estado"] = "Un anuncio no puede cancelarse ni finalizarse."
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return self.titulo


# TODO(publicaciones-clases): vincular publicaciones con clases cuando el módulo
# defina división etaria. No se persiste división etaria en Publicacion.
