from django.urls import path

from . import views

app_name = "publicaciones"

urlpatterns = [
    path("", views.publicacion_list, name="publicacion_list"),
    path("nueva/", views.publicacion_create, name="publicacion_create"),
    path("<int:publicacion_id>/", views.publicacion_detail, name="publicacion_detail"),
    path("<int:publicacion_id>/editar/", views.publicacion_update, name="publicacion_update"),
    path("<int:publicacion_id>/publicar/", views.publicacion_publicar, name="publicacion_publicar"),
    path("<int:publicacion_id>/cancelar/", views.publicacion_cancelar, name="publicacion_cancelar"),
    path("<int:publicacion_id>/finalizar/", views.publicacion_finalizar, name="publicacion_finalizar"),
    path("<int:publicacion_id>/desactivar/", views.publicacion_desactivar, name="publicacion_desactivar"),
]
