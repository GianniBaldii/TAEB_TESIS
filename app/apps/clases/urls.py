from django.urls import path

from . import views

app_name = "clases"

urlpatterns = [
    path("", views.clase_list, name="clase_list"),
    path("calendario/", views.calendario, name="calendario"),
    path("nueva/", views.clase_create, name="clase_create"),
    path("<int:clase_id>/", views.clase_detail, name="clase_detail"),
    path("<int:clase_id>/editar/", views.clase_update, name="clase_update"),
    path("<int:clase_id>/activar/", views.clase_estado, {"activar": True}, name="clase_activar"),
    path("<int:clase_id>/desactivar/", views.clase_estado, {"activar": False}, name="clase_desactivar"),
    path("<int:clase_id>/horarios/nuevo/", views.horario_create, name="horario_create"),
    path("horarios/<int:horario_id>/editar/", views.horario_update, name="horario_update"),
    path("horarios/<int:horario_id>/desactivar/", views.horario_desactivar, name="horario_desactivar"),
    path("horarios/<int:horario_id>/abrir/", views.abrir_ocurrencia, name="abrir_ocurrencia"),
    path("<int:clase_id>/alumnos/agregar/", views.clase_alumno_create, name="clase_alumno_create"),
    path("inscripciones/<int:clase_alumno_id>/dar-baja/", views.clase_alumno_baja, name="clase_alumno_baja"),
    path("inscripciones/<int:clase_alumno_id>/reactivar/", views.clase_alumno_reactivar, name="clase_alumno_reactivar"),
    path("<int:clase_id>/sesiones/extra/nueva/", views.clase_extra_create, name="clase_extra_create"),
    path("sesiones/<int:sesion_id>/", views.sesion_detail, name="sesion_detail"),
    path("sesiones/<int:sesion_id>/asistencia/", views.asistencia_form, name="asistencia_form"),
    path("sesiones/<int:sesion_id>/asistencia/marcar-todos-presentes/", views.marcar_todos_presentes, name="marcar_todos_presentes"),
    path("sesiones/<int:sesion_id>/cerrar/", views.cerrar_asistencia, name="cerrar_asistencia"),
    path("sesiones/<int:sesion_id>/reabrir/", views.reabrir_asistencia, name="reabrir_asistencia"),
    path("sesiones/<int:sesion_id>/cancelar/", views.cancelar_sesion, name="cancelar_sesion"),
]
