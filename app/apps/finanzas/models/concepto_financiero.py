from django.db import models


class ConceptoFinanciero(models.Model):
    class Codigo(models.TextChoices):
        CUOTA = "CUOTA", "Cuota"
        EXAMEN = "EXAMEN", "Examen"
        TORNEO = "TORNEO", "Torneo"

    escuela = models.ForeignKey("escuelas.Escuela", on_delete=models.PROTECT, related_name="conceptos_financieros", db_column="id_escuela")
    codigo = models.CharField(max_length=20, choices=Codigo.choices)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "finanzas_conceptos"
        ordering = ["codigo"]
        constraints = [models.UniqueConstraint(fields=["escuela", "codigo"], name="uq_finanzas_concepto_escuela_codigo")]

    def __str__(self):
        return f"{self.nombre} - {self.escuela}"
