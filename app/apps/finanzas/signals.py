from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.escuelas.models import Escuela
from .models import ConceptoFinanciero


@receiver(post_save, sender=Escuela)
def crear_conceptos_financieros_de_escuela(sender, instance, created, **kwargs):
    if not created:
        return
    for codigo, nombre in (
        (ConceptoFinanciero.Codigo.CUOTA, "Cuota"),
        (ConceptoFinanciero.Codigo.EXAMEN, "Examen"),
        (ConceptoFinanciero.Codigo.TORNEO, "Torneo"),
    ):
        ConceptoFinanciero.objects.get_or_create(
            escuela=instance,
            codigo=codigo,
            defaults={"nombre": nombre, "activo": True},
        )
