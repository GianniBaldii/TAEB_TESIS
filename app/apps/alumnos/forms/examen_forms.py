from django import forms

from ..models import Cinturon
from .base import INPUT_CLASS


class CrearExamenForm(forms.Form):
    fecha_examen = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    lugar = forms.CharField(max_length=150, required=False)
    es_historico = forms.BooleanField(required=False, label="Carga historica", help_text="Usar para examenes ya rendidos antes de cargar el alumno en TAEB.")
    cinturon_destino = forms.ModelChoiceField(queryset=Cinturon.objects.filter(activo=True), required=False, label="Cinturon destino")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)
        self.fields["es_historico"].widget.attrs["x-model"] = "historico"

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("es_historico") and not cleaned_data.get("cinturon_destino"):
            self.add_error("cinturon_destino", "Seleccione el cinturón destino para el examen histórico.")
        return cleaned_data
