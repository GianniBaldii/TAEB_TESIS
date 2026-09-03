from django.urls import path
from . import views

app_name = "finanzas"
urlpatterns = [
    path("cuotas/", views.cuota_list, name="cuota_list"),
    path("cuotas/generar/", views.generar_cuotas, name="generar_cuotas"),
    path("cobros/generar/", views.generar_cobro, name="generar_cobro"),
    path("configuracion/", views.configuracion, name="configuracion"),
    path("conceptos/<int:pk>/toggle/", views.toggle_concepto, name="toggle_concepto"),
    path("obligaciones/<int:pk>/", views.obligacion_detail, name="obligacion_detail"),
    path("obligaciones/<int:pk>/pagar/", views.registrar_pago, name="registrar_pago"),
    path("cuentas/<int:inscripcion_id>/", views.cuenta_corriente, name="cuenta_corriente"),
]
