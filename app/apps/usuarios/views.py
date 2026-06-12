from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import LoginForm


class UsuarioLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "autenticacion/login.html"
    redirect_authenticated_user = True


class UsuarioLogoutView(LogoutView):
    next_page = reverse_lazy("usuarios:login")
