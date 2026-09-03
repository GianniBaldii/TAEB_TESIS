from django.contrib import admin
from .models import ConceptoFinanciero, ConfiguracionCuota, ObligacionPago, Pago, PagoAplicacion

admin.site.register([ConceptoFinanciero, ConfiguracionCuota, ObligacionPago, Pago, PagoAplicacion])
