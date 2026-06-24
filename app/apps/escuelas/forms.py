from django import forms
from django.contrib.auth.password_validation import validate_password

from apps.escuelas.models import Escuela, EscuelaDocente


class EscuelaForm(forms.ModelForm):
    class Meta:
        model = Escuela
        fields = ["nombre", "nombre_comercial", "razon_social", "cuit", "email", "telefono", "direccion", "ciudad", "provincia"]


class DocenteAltaForm(forms.Form):
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    username = forms.CharField(label="Usuario")
    email = forms.EmailField(required=False)
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)
    dni = forms.CharField(label="DNI")
    telefono = forms.CharField(required=False)
    fecha_nacimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    escuela = forms.ModelChoiceField(queryset=Escuela.objects.filter(activo=True))
    rol = forms.ChoiceField(choices=EscuelaDocente.Rol.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = "block w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", input_class)
        self.fields["password1"].widget.attrs["x-bind:type"] = "mostrarContrasena ? 'text' : 'password'"
        self.fields["password2"].widget.attrs["x-bind:type"] = "mostrarContrasena ? 'text' : 'password'"

    def clean_username(self):
        from django.contrib.auth import get_user_model
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username=username).exists():
            raise forms.ValidationError("Este usuario ya está registrado.")
        return username

    def clean(self):
        data = super().clean()
        if data.get("password1") != data.get("password2"):
            self.add_error("password2", "Las contraseñas no coinciden.")
        if data.get("password1"):
            validate_password(data["password1"])
        return data


class DocenteEscuelaForm(forms.Form):
    escuela = forms.ModelChoiceField(queryset=Escuela.objects.filter(activo=True))
    rol = forms.ChoiceField(choices=EscuelaDocente.Rol.choices)
