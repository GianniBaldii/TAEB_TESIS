from django import forms

from ..models import Alumno
from .base import TailwindModelForm


class AlumnoForm(TailwindModelForm):
    class Meta:
        model = Alumno
        fields = ["nombre", "apellido", "dni", "fecha_nacimiento", "fecha_inicio_taekwondo",
                  "email", "telefono", "direccion", "peso_aproximado", "altura_aproximada",
                  "cinturon_actual", "activo"]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "fecha_inicio_taekwondo": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_inicio_taekwondo"].label = "Fecha de inicio en Taekwondo"
        self.fields["cinturon_actual"].help_text = (
            "Déjelo vacío para asignar automáticamente el cinturón inicial. "
            "Seleccione otro solo si viene de otra escuela."
        )
