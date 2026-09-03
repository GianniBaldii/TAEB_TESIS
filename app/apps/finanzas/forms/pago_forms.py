from django import forms

from ..models import Pago
from .base import TailwindFormMixin


class PagoForm(TailwindFormMixin, forms.Form):
    monto = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    metodo = forms.ChoiceField(choices=Pago.Metodo.choices)
    fecha_pago = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    referencia = forms.CharField(max_length=150, required=False)
    observaciones = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
