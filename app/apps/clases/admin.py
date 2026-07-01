from django.contrib import admin

from .models import AsistenciaClase, Clase, ClaseAlumno, ClaseHorario, ClaseSesion


class ClaseHorarioInline(admin.TabularInline):
    model = ClaseHorario
    extra = 0


@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ("nombre", "escuela", "docente_responsable", "cupo_maximo", "activo")
    list_filter = ("activo", "escuela")
    search_fields = ("nombre", "escuela__nombre", "escuela__nombre_comercial")
    inlines = [ClaseHorarioInline]


@admin.register(ClaseHorario)
class ClaseHorarioAdmin(admin.ModelAdmin):
    list_display = ("clase", "dia_semana", "hora_inicio", "hora_fin", "activo")
    list_filter = ("activo", "dia_semana", "clase__escuela")
    search_fields = ("clase__nombre",)


@admin.register(ClaseAlumno)
class ClaseAlumnoAdmin(admin.ModelAdmin):
    list_display = ("clase", "alumno_escuela", "activo", "fecha_alta", "fecha_baja")
    list_filter = ("activo", "clase__escuela")
    search_fields = (
        "clase__nombre",
        "alumno_escuela__alumno__nombre",
        "alumno_escuela__alumno__apellido",
        "alumno_escuela__alumno__dni",
    )


@admin.register(ClaseSesion)
class ClaseSesionAdmin(admin.ModelAdmin):
    list_display = ("clase", "fecha", "hora_inicio", "hora_fin", "estado", "es_clase_extra")
    list_filter = ("estado", "es_clase_extra", "clase__escuela", "fecha")
    search_fields = ("clase__nombre",)
    date_hierarchy = "fecha"


@admin.register(AsistenciaClase)
class AsistenciaClaseAdmin(admin.ModelAdmin):
    list_display = ("sesion", "clase_alumno", "estado", "registrado_por", "fecha_modificacion")
    list_filter = ("estado", "sesion__clase__escuela", "sesion__fecha")
    search_fields = (
        "sesion__clase__nombre",
        "clase_alumno__alumno_escuela__alumno__nombre",
        "clase_alumno__alumno_escuela__alumno__apellido",
        "clase_alumno__alumno_escuela__alumno__dni",
    )
