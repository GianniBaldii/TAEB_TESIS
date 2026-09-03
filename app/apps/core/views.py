from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from .selectors import resumen_dashboard


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return redirect("usuarios:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "tablero/inicio.html"
    extra_context = {"titulo_pagina": "Inicio"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(resumen_dashboard(self.request.user))
        return context
