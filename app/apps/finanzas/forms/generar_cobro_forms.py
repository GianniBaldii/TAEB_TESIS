from django import forms
from django.db import models

from ..models import ConceptoFinanciero
from ..selectors.finanzas_selectors import alumnos_activos, clases_activas
from .base import TailwindFormMixin


class GenerarCuotasForm(TailwindFormMixin, forms.Form):
    class Destino(models.TextChoices):
        TODOS = "TODOS", "Todos los alumnos activos"
        CLASE = "CLASE", "Alumnos de una clase"
        MANUAL = "MANUAL", "Selección manual"

    periodo = forms.CharField(widget=forms.DateInput(attrs={"type": "month"}))
    destino = forms.ChoiceField(choices=Destino.choices, widget=forms.RadioSelect)
    clase = forms.ModelChoiceField(queryset=None, required=False)
    alumnos = forms.ModelMultipleChoiceField(queryset=None, required=False)
    monto = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    dias_tolerancia = forms.IntegerField(min_value=0)

    def __init__(self, *args, escuela, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["clase"].queryset = clases_activas(escuela)
        self.fields["alumnos"].queryset = alumnos_activos(escuela)
        self.fields["alumnos"].widget.attrs["size"] = 8
        self.fields["alumnos"].help_text = "Usá Ctrl (Windows) o Cmd (Mac) para seleccionar varios alumnos."

    def clean(self):
        datos = super().clean()
        if datos.get("destino") == self.Destino.CLASE and not datos.get("clase"):
            self.add_error("clase", "Seleccioná una clase.")
        if datos.get("destino") == self.Destino.MANUAL and not datos.get("alumnos"):
            self.add_error("alumnos", "Seleccioná al menos un alumno.")
        return datos


class GenerarCobroForm(TailwindFormMixin, forms.Form):
    concepto = forms.ModelChoiceField(queryset=None)
    alumnos = forms.ModelMultipleChoiceField(queryset=None)
    monto = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    dias_tolerancia = forms.IntegerField(min_value=0, initial=0)
    descripcion = forms.CharField(max_length=255)

    def __init__(self, *args, escuela, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["concepto"].queryset = ConceptoFinanciero.objects.filter(escuela=escuela, activo=True, codigo__in=[ConceptoFinanciero.Codigo.EXAMEN, ConceptoFinanciero.Codigo.TORNEO])
        self.fields["alumnos"].queryset = alumnos_activos(escuela)
        self.fields["alumnos"].widget.attrs["size"] = 9
        self.fields["alumnos"].help_text = "Seleccioná uno o varios alumnos con Ctrl/Cmd."
