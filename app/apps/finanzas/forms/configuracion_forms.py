from django import forms

from ..models import ConfiguracionCuota
from .base import TailwindFormMixin


class ConfiguracionCuotaForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = ConfiguracionCuota
        fields = ["monto_actual", "dia_vencimiento", "dias_tolerancia", "activa"]
