from django.db import models

from .cinturon import Cinturon


class ExamenTemplate(models.Model):
    cinturon = models.ForeignKey(
        Cinturon, on_delete=models.PROTECT, related_name="templates_examen"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    nota_minima_aprobacion = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    version = models.PositiveSmallIntegerField(default=1)
    template_origen = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="versiones_derivadas",
    )
    vigente_desde = models.DateField(null=True, blank=True)
    vigente_hasta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["cinturon__orden", "nombre", "-version"]
        verbose_name = "Template de examen"
        verbose_name_plural = "Templates de examenes"

    def __str__(self):
        return f"{self.nombre} v{self.version} - {self.cinturon}"


class ExamenTemplateSeccion(models.Model):
    examen_template = models.ForeignKey(
        ExamenTemplate, on_delete=models.CASCADE, related_name="secciones"
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    orden = models.PositiveSmallIntegerField(default=1)
    obligatorio = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        constraints = [
            models.UniqueConstraint(
                fields=["examen_template", "nombre"],
                name="seccion_template_nombre_unicos",
            )
        ]
        verbose_name = "Seccion de template"
        verbose_name_plural = "Secciones de template"

    def __str__(self):
        return f"{self.examen_template} - {self.nombre}"


class ExamenTemplateItem(models.Model):
    class TipoEvaluacion(models.TextChoices):
        NUMERICA = "NUMERICA", "Numerica"
        CONCEPTO = "CONCEPTO", "Concepto"
        TEXTO = "TEXTO", "Texto"
        CHECK = "CHECK", "Check"

    seccion = models.ForeignKey(
        ExamenTemplateSeccion, on_delete=models.CASCADE, related_name="items"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    tipo_evaluacion = models.CharField(
        max_length=10, choices=TipoEvaluacion.choices
    )
    orden = models.PositiveSmallIntegerField(default=1)
    puntaje_maximo = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    ponderacion = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    obligatorio = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["seccion__orden", "orden"]
        verbose_name = "Item de template"
        verbose_name_plural = "Items de template"

    def __str__(self):
        return f"{self.seccion} - {self.nombre}"
