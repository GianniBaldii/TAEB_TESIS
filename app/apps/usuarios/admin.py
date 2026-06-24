from django.contrib import admin

from .models import Docente


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "dni", "telefono", "activo")
    list_filter = ("activo",)
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name", "dni")
    autocomplete_fields = ("usuario",)
