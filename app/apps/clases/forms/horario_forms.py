from django import forms
from ..models import ClaseHorario
from .base import TailwindModelForm
class ClaseHorarioForm(TailwindModelForm):
    class Meta:
        model = ClaseHorario
        fields = ["dia_semana", "hora_inicio", "hora_fin", "fecha_desde", "fecha_hasta", "activo"]
        widgets = {"hora_inicio": forms.TimeInput(attrs={"type": "time"}), "hora_fin": forms.TimeInput(attrs={"type": "time"}), "fecha_desde": forms.DateInput(attrs={"type": "date"}), "fecha_hasta": forms.DateInput(attrs={"type": "date"})}
