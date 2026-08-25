from django import forms

from ..models import ExamenTemplate, ExamenTemplateItem, ExamenTemplateSeccion
from .base import TailwindModelForm


class ExamenTemplateForm(TailwindModelForm):
    class Meta:
        model = ExamenTemplate
        fields = ["cinturon", "nombre", "descripcion", "nota_minima_aprobacion", "vigente_desde", "vigente_hasta"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3}), "vigente_desde": forms.DateInput(attrs={"type": "date"}), "vigente_hasta": forms.DateInput(attrs={"type": "date"})}


class ExamenTemplateSeccionForm(TailwindModelForm):
    class Meta:
        model = ExamenTemplateSeccion
        fields = ["nombre", "descripcion", "orden", "obligatorio", "activo"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}


class ExamenTemplateItemForm(TailwindModelForm):
    class Meta:
        model = ExamenTemplateItem
        fields = ["nombre", "descripcion", "tipo_evaluacion", "orden", "puntaje_maximo", "ponderacion", "obligatorio", "activo"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}
