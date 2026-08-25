from django import forms
from ..models import Escuela
from .base import aplicar_estilos_campos

class EscuelaForm(forms.ModelForm):
    class Meta:
        model = Escuela
        fields = ["nombre", "nombre_comercial", "razon_social", "cuit", "email", "telefono", "direccion", "ciudad", "provincia"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos_campos(self.fields)
