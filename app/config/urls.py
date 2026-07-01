from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("administracion/", include("apps.escuelas.urls")),
    path("alumnos/", include("apps.alumnos.urls")),
    path("clases/", include("apps.clases.urls")),
    path("api/v1/mobile/", include("apps.api_mobile.urls")),
    path("", include("apps.core.urls")),
    path("", include("apps.usuarios.urls")),
]
