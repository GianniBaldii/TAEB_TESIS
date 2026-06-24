from django.contrib import admin

from .models import Escuela, EscuelaDocente


@admin.register(Escuela)
class EscuelaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ciudad", "provincia", "telefono", "activo")
    list_filter = ("activo", "provincia")
    search_fields = ("nombre", "nombre_comercial", "cuit", "ciudad")


@admin.register(EscuelaDocente)
class EscuelaDocenteAdmin(admin.ModelAdmin):
    list_display = ("docente", "escuela", "rol", "activo", "fecha_alta")
    list_filter = ("activo", "rol", "escuela")
    search_fields = ("docente__usuario__username", "docente__dni", "escuela__nombre")
    autocomplete_fields = ("docente", "escuela")
