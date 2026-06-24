from django.urls import path

from . import views

app_name = "escuelas"

urlpatterns = [
    path("escuelas/", views.escuela_list, name="escuela_list"),
    path("escuelas/nueva/", views.escuela_create, name="escuela_create"),
    path("escuelas/<int:pk>/editar/", views.escuela_update, name="escuela_update"),
    path("escuelas/<int:pk>/activar/", views.escuela_estado, {"activar": True}, name="escuela_activar"),
    path("escuelas/<int:pk>/desactivar/", views.escuela_estado, {"activar": False}, name="escuela_desactivar"),
    path("docentes/", views.docente_list, name="docente_list"),
    path("docentes/nuevo/", views.docente_create, name="docente_create"),
    path("docentes/<int:pk>/", views.docente_detail, name="docente_detail"),
    path("docentes/<int:pk>/activar/", views.docente_estado, {"activar": True}, name="docente_activar"),
    path("docentes/<int:pk>/desactivar/", views.docente_estado, {"activar": False}, name="docente_desactivar"),
    path("docentes/<int:pk>/escuelas/nueva/", views.docente_escuela_create, name="docente_escuela_create"),
    path("docentes/relaciones/<int:pk>/activar/", views.docente_escuela_estado, {"activar": True}, name="docente_escuela_activar"),
    path("docentes/relaciones/<int:pk>/desactivar/", views.docente_escuela_estado, {"activar": False}, name="docente_escuela_desactivar"),
]
