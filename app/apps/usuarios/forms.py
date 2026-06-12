from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "class": (
                    "block w-full rounded-lg border border-white/25 bg-white/5 "
                    "py-3 pl-11 pr-4 text-sm text-white outline-none "
                    "transition placeholder:text-slate-400 "
                    "focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
                ),
                "placeholder": "Ingresá tu usuario",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": (
                    "block w-full rounded-lg border border-white/25 bg-white/5 "
                    "py-3 pl-11 pr-12 text-sm text-white outline-none "
                    "transition placeholder:text-slate-400 "
                    "focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
                ),
                "placeholder": "Ingresá tu contraseña",
                "x-bind:type": "mostrarContrasena ? 'text' : 'password'",
            }
        ),
    )
