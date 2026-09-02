from django.contrib import admin

from .models import Publicacion


@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "escuela",
        "tipo_publicacion",
        "tematica",
        "estado",
        "fecha_hora_inicio",
        "activo",
        "creado_por",
    )
    list_filter = ("escuela", "tipo_publicacion", "tematica", "estado", "activo")
    search_fields = ("titulo", "descripcion", "ubicacion", "escuela__nombre")
    date_hierarchy = "fecha_creacion"
