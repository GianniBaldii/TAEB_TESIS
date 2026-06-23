from django.urls import path

from . import views

app_name = "alumnos"

urlpatterns = [
    path("", views.alumno_list, name="alumno_list"),
    path("nuevo/", views.alumno_create, name="alumno_create"),
    path("<int:pk>/", views.alumno_detail, name="alumno_detail"),
    path("<int:pk>/editar/", views.alumno_update, name="alumno_update"),
    path("<int:pk>/baja/", views.alumno_baja, name="alumno_baja"),
    path("<int:pk>/reactivar/", views.alumno_reactivar, name="alumno_reactivar"),
    path("<int:alumno_id>/examenes/nuevo/", views.examen_create, name="examen_create"),
    path(
        "<int:alumno_id>/examenes/<int:examen_id>/",
        views.examen_detail,
        name="examen_detail",
    ),
    path(
        "<int:alumno_id>/examenes/<int:examen_id>/evaluaciones/",
        views.examen_evaluaciones,
        name="examen_evaluaciones",
    ),
    path(
        "<int:alumno_id>/examenes/<int:examen_id>/aprobar/",
        views.examen_aprobar,
        name="examen_aprobar",
    ),
    path(
        "<int:alumno_id>/examenes/<int:examen_id>/desaprobar/",
        views.examen_desaprobar,
        name="examen_desaprobar",
    ),
    path(
        "<int:alumno_id>/examenes/<int:examen_id>/anular/",
        views.examen_anular,
        name="examen_anular",
    ),
    path("templates-examen/", views.template_list, name="template_list"),
    path("templates-examen/nuevo/", views.template_create, name="template_create"),
    path("templates-examen/<int:pk>/", views.template_detail, name="template_detail"),
    path(
        "templates-examen/<int:pk>/editar/",
        views.template_update,
        name="template_update",
    ),
    path(
        "templates-examen/<int:pk>/duplicar/",
        views.template_duplicar,
        name="template_duplicar",
    ),
    path(
        "templates-examen/<int:pk>/activar/",
        views.template_activar,
        name="template_activar",
    ),
    path(
        "templates-examen/<int:pk>/desactivar/",
        views.template_desactivar,
        name="template_desactivar",
    ),
    path(
        "templates-examen/<int:pk>/eliminar/",
        views.template_eliminar,
        name="template_eliminar",
    ),
    path(
        "templates-examen/<int:template_id>/secciones/nueva/",
        views.seccion_create,
        name="seccion_create",
    ),
    path(
        "templates-examen/secciones/<int:seccion_id>/editar/",
        views.seccion_update,
        name="seccion_update",
    ),
    path(
        "templates-examen/secciones/<int:seccion_id>/desactivar/",
        views.seccion_desactivar,
        name="seccion_desactivar",
    ),
    path(
        "templates-examen/secciones/<int:seccion_id>/items/nuevo/",
        views.item_create,
        name="item_create",
    ),
    path(
        "templates-examen/items/<int:item_id>/editar/",
        views.item_update,
        name="item_update",
    ),
    path(
        "templates-examen/items/<int:item_id>/desactivar/",
        views.item_desactivar,
        name="item_desactivar",
    ),
]
