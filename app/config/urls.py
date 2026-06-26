from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("administracion/", include("apps.escuelas.urls")),
    path("alumnos/", include("apps.alumnos.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.usuarios.urls")),
]
