from django.db import transaction

from apps.escuelas.services.acceso_escuela_service import validar_acceso_a_escuela
from ..models import ConceptoFinanciero, ConfiguracionCuota


CONCEPTOS_INICIALES = {
    ConceptoFinanciero.Codigo.CUOTA: "Cuota",
    ConceptoFinanciero.Codigo.EXAMEN: "Examen",
    ConceptoFinanciero.Codigo.TORNEO: "Torneo",
}


@transaction.atomic
def asegurar_conceptos(escuela):
    return [ConceptoFinanciero.objects.get_or_create(escuela=escuela, codigo=codigo, defaults={"nombre": nombre, "activo": True})[0] for codigo, nombre in CONCEPTOS_INICIALES.items()]


@transaction.atomic
def guardar_configuracion_cuota(*, escuela, datos, usuario):
    validar_acceso_a_escuela(usuario, escuela)
    asegurar_conceptos(escuela)
    configuracion, _ = ConfiguracionCuota.objects.update_or_create(escuela=escuela, defaults=datos)
    return configuracion


@transaction.atomic
def cambiar_estado_concepto(*, concepto, activo, usuario):
    validar_acceso_a_escuela(usuario, concepto.escuela)
    concepto.activo = activo
    concepto.save(update_fields=["activo", "fecha_modificacion"])
    return concepto
