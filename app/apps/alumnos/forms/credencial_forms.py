from django import forms

from .base import INPUT_CLASS


class GenerarCredencialesAlumnoForm(forms.Form):
    password = forms.CharField(label="Contrasena inicial", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password_confirmacion = forms.CharField(label="Confirmar contrasena", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)


class ResetearPasswordAlumnoForm(GenerarCredencialesAlumnoForm):
    password = forms.CharField(label="Nueva contrasena", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password_confirmacion = forms.CharField(label="Confirmar nueva contrasena", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))


class BloquearAccesoMobileAlumnoForm(forms.Form):
    motivo = forms.CharField(required=False, label="Motivo", widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)
