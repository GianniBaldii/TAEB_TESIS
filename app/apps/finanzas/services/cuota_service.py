import calendar
from datetime import date

from ..models import ConceptoFinanciero, ConfiguracionCuota
from .excepciones import FinanzasError
from .obligacion_service import crear_obligaciones

MESES = ("", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")


def fecha_vencimiento_periodo(anio, mes, dia):
    return date(anio, mes, min(dia, calendar.monthrange(anio, mes)[1]))


def generar_cuotas_periodo(*, escuela, alumnos_escuela, anio, mes, monto, fecha_vencimiento, dias_tolerancia, usuario):
    alumnos_escuela = list(alumnos_escuela)
    try:
        configuracion = ConfiguracionCuota.objects.get(escuela=escuela, activa=True)
        concepto = ConceptoFinanciero.objects.get(escuela=escuela, codigo=ConceptoFinanciero.Codigo.CUOTA, activo=True)
    except (ConfiguracionCuota.DoesNotExist, ConceptoFinanciero.DoesNotExist) as exc:
        raise FinanzasError("La cuota no está configurada o su concepto está inactivo.") from exc
    if not configuracion.activa:
        raise FinanzasError("La configuración de cuota está inactiva.")
    claves = {i.pk: f"CUOTA:{i.pk}:{anio:04d}-{mes:02d}" for i in alumnos_escuela}
    return crear_obligaciones(
        escuela=escuela, concepto=concepto, alumnos_escuela=alumnos_escuela,
        monto=monto, fecha_vencimiento=fecha_vencimiento, dias_tolerancia=dias_tolerancia,
        descripcion=f"Cuota {MESES[mes]} {anio}", usuario=usuario,
        claves_origen=claves, periodo_anio=anio, periodo_mes=mes,
    )
