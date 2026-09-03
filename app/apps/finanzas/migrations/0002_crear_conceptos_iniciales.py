from django.db import migrations


def crear_conceptos(apps, schema_editor):
    Escuela = apps.get_model("escuelas", "Escuela")
    Concepto = apps.get_model("finanzas", "ConceptoFinanciero")
    conceptos = (("CUOTA", "Cuota"), ("EXAMEN", "Examen"), ("TORNEO", "Torneo"))
    for escuela in Escuela.objects.all():
        for codigo, nombre in conceptos:
            Concepto.objects.get_or_create(escuela=escuela, codigo=codigo, defaults={"nombre": nombre, "activo": True})


def eliminar_conceptos_sin_uso(apps, schema_editor):
    Concepto = apps.get_model("finanzas", "ConceptoFinanciero")
    Concepto.objects.filter(codigo__in=["CUOTA", "EXAMEN", "TORNEO"], obligaciones__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("finanzas", "0001_initial")]
    operations = [migrations.RunPython(crear_conceptos, eliminar_conceptos_sin_uso)]
