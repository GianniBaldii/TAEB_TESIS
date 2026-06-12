from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return redirect("usuarios:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "tablero/inicio.html"
    extra_context = {"titulo_pagina": "Inicio"}
