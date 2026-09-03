from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.alumnos.models import Alumno, AlumnoEscuela
from apps.escuelas.models import Escuela, EscuelaDocente
from apps.usuarios.models import Docente
from apps.finanzas.models import ConfiguracionCuota, ObligacionPago


class FinanzasViewsTests(TestCase):
    def setUp(self):
        self.escuela = Escuela.objects.create(nombre="TAEB Web")
        self.usuario = get_user_model().objects.create_user(username="finanzas", password="test")
        docente = Docente.objects.create(usuario=self.usuario, dni="view-1")
        EscuelaDocente.objects.create(escuela=self.escuela, docente=docente)
        alumno = Alumno.objects.create(nombre="Ana", apellido="Prueba", dni="view-2")
        self.inscripcion = AlumnoEscuela.objects.create(escuela=self.escuela, alumno=alumno)
        self.client.force_login(self.usuario)

    def test_pantallas_principales_responden(self):
        for nombre in ("finanzas:cuota_list", "finanzas:configuracion", "finanzas:generar_cobro"):
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

    def test_selector_destinatarios_renderiza_estado_alpine_valido(self):
        respuesta = self.client.get(reverse("finanzas:generar_cuotas"))
        self.assertContains(respuesta, 'x-data=\'{ "destino": "TODOS"')
        self.assertContains(respuesta, '@click="destino = \'CLASE\'"')
        self.assertContains(respuesta, '@click="destino = \'MANUAL\'"')

    def test_configura_y_genera_cuota_desde_interfaz(self):
        respuesta = self.client.post(reverse("finanzas:configuracion"), {"monto_actual": "35000.00", "dia_vencimiento": 10, "dias_tolerancia": 5, "activa": "on"})
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(ConfiguracionCuota.objects.filter(escuela=self.escuela, monto_actual=Decimal("35000")).exists())
        respuesta = self.client.post(reverse("finanzas:generar_cuotas"), {"periodo": "2026-09", "destino": "TODOS", "monto": "35000.00", "fecha_vencimiento": "2026-09-10", "dias_tolerancia": 5})
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(ObligacionPago.objects.filter(alumno_escuela=self.inscripcion).count(), 1)

    def test_detalle_y_cuenta_corriente_respetan_escuela(self):
        self.client.post(reverse("finanzas:configuracion"), {"monto_actual": "35000", "dia_vencimiento": 10, "dias_tolerancia": 5, "activa": "on"})
        self.client.post(reverse("finanzas:generar_cuotas"), {"periodo": "2026-09", "destino": "TODOS", "monto": "35000", "fecha_vencimiento": "2026-09-10", "dias_tolerancia": 5})
        obligacion = ObligacionPago.objects.get()
        self.assertEqual(self.client.get(reverse("finanzas:obligacion_detail", args=[obligacion.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("finanzas:cuenta_corriente", args=[self.inscripcion.pk])).status_code, 200)
