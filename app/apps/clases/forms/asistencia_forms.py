from django import forms
from apps.alumnos.models import AlumnoEscuela
from ..models import AsistenciaClase
from .base import INPUT_CLASS
class ClaseAlumnoForm(forms.Form):
    alumno_escuela = forms.ModelChoiceField(queryset=AlumnoEscuela.objects.none())
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    def __init__(self, *args, alumnos_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["alumno_escuela"].queryset = alumnos_queryset or AlumnoEscuela.objects.none()
        for field in self.fields.values(): field.widget.attrs.setdefault("class", INPUT_CLASS)
class CancelarSesionForm(forms.Form):
    motivo = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "class": INPUT_CLASS}))
class AsistenciaLineaForm(forms.Form):
    estado = forms.ChoiceField(choices=AsistenciaClase.Estado.choices)
    observaciones = forms.CharField(required=False)
