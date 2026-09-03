from .cobro_views import generar_cobro
from .cuota_views import cuota_list, generar_cuotas
from .finanzas_views import configuracion, cuenta_corriente, obligacion_detail, toggle_concepto
from .pago_views import registrar_pago

__all__ = ["configuracion", "cuenta_corriente", "generar_cobro", "generar_cuotas", "obligacion_detail", "cuota_list", "registrar_pago", "toggle_concepto"]
