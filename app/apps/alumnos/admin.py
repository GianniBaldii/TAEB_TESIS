"""Administrador del modulo de alumnos."""

from django.contrib import admin

from .models import (
    Alumno,
    AlumnoCinturonHistorial,
    Cinturon,
    Examen,
    ExamenDetalle,
    ExamenTemplate,
    ExamenTemplateItem,
    ExamenTemplateSeccion,
)


@admin.register(Cinturon)
class CinturonAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre", "color", "tipo_rango", "numeracion", "activo")
    list_filter = ("tipo_rango", "activo")
    search_fields = ("nombre", "color")
    ordering = ("orden",)


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = (
        "apellido",
        "nombre",
        "dni",
        "cinturon_actual",
        "telefono",
        "activo",
    )
    list_filter = ("activo", "cinturon_actual")
    search_fields = ("nombre", "apellido", "dni", "email", "telefono")
    autocomplete_fields = ("cinturon_actual",)
    ordering = ("apellido", "nombre")


class ExamenTemplateItemInline(admin.TabularInline):
    model = ExamenTemplateItem
    extra = 0
    fields = (
        "orden",
        "nombre",
        "tipo_evaluacion",
        "puntaje_maximo",
        "ponderacion",
        "obligatorio",
        "activo",
    )


@admin.register(ExamenTemplateSeccion)
class ExamenTemplateSeccionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "examen_template", "orden", "obligatorio", "activo")
    list_filter = ("activo", "obligatorio", "examen_template__cinturon")
    search_fields = ("nombre", "examen_template__nombre")
    autocomplete_fields = ("examen_template",)
    inlines = (ExamenTemplateItemInline,)


class ExamenTemplateSeccionInline(admin.TabularInline):
    model = ExamenTemplateSeccion
    extra = 0
    fields = ("orden", "nombre", "obligatorio", "activo")


@admin.register(ExamenTemplate)
class ExamenTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "cinturon",
        "version",
        "nota_minima_aprobacion",
        "activo",
    )
    list_filter = ("activo", "cinturon__tipo_rango", "cinturon")
    search_fields = ("nombre", "descripcion", "cinturon__nombre")
    autocomplete_fields = ("cinturon",)
    inlines = (ExamenTemplateSeccionInline,)


@admin.register(ExamenTemplateItem)
class ExamenTemplateItemAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "seccion",
        "tipo_evaluacion",
        "orden",
        "obligatorio",
        "activo",
    )
    list_filter = ("tipo_evaluacion", "activo", "obligatorio")
    search_fields = ("nombre", "descripcion", "seccion__nombre")
    autocomplete_fields = ("seccion",)


class ExamenDetalleInline(admin.TabularInline):
    model = ExamenDetalle
    extra = 0
    autocomplete_fields = ("template_item",)


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = (
        "alumno",
        "fecha_examen",
        "cinturon_origen",
        "cinturon_destino",
        "estado",
        "nota_final",
    )
    list_filter = ("estado", "fecha_examen", "cinturon_destino")
    search_fields = ("alumno__nombre", "alumno__apellido", "alumno__dni", "lugar")
    autocomplete_fields = (
        "alumno",
        "examen_template",
        "cinturon_origen",
        "cinturon_destino",
    )
    inlines = (ExamenDetalleInline,)


@admin.register(ExamenDetalle)
class ExamenDetalleAdmin(admin.ModelAdmin):
    list_display = ("examen", "template_item", "nota_numerica", "concepto", "aprobado")
    list_filter = ("template_item__tipo_evaluacion", "aprobado")
    search_fields = ("examen__alumno__apellido", "template_item__nombre", "concepto")
    autocomplete_fields = ("examen", "template_item")


@admin.register(AlumnoCinturonHistorial)
class AlumnoCinturonHistorialAdmin(admin.ModelAdmin):
    list_display = ("alumno", "cinturon", "fecha_obtencion", "examen")
    list_filter = ("cinturon", "fecha_obtencion")
    search_fields = ("alumno__nombre", "alumno__apellido", "alumno__dni")
    autocomplete_fields = ("alumno", "cinturon", "examen")
