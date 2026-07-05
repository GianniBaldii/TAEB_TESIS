from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.alumnos.models import Alumno, AlumnoEscuela
from apps.alumnos.services import alumno_credencial_service
from apps.escuelas.models import Escuela


class MobileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.superadmin = get_user_model().objects.create_superuser(
            "admin",
            "admin@example.com",
            "clave-segura",
        )
        self.escuela = Escuela.objects.create(nombre="Escuela A")
        self.alumno = Alumno.objects.create(
            nombre="Juan",
            apellido="Perez",
            dni="40123456",
            activo=True,
        )
        AlumnoEscuela.objects.create(alumno=self.alumno, escuela=self.escuela)
        self.credencial = alumno_credencial_service.crear_credencial_mobile_para_alumno(
            alumno=self.alumno,
            password="ClaveSegura123!",
            password_confirmacion="ClaveSegura123!",
            actor=self.superadmin,
        )

    def test_login_mobile_devuelve_tokens_y_me(self):
        response = self.client.post(
            "/api/v1/mobile/auth/login/",
            {"dni": "40.123.456", "password": "ClaveSegura123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        me_response = self.client.get("/api/v1/mobile/me/")

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["nombre_completo"], "Juan Perez")

    def test_login_fallido_incrementa_intentos(self):
        response = self.client.post(
            "/api/v1/mobile/auth/login/",
            {"dni": "40123456", "password": "incorrecta"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.credencial.refresh_from_db()
        self.assertEqual(self.credencial.intentos_fallidos, 1)

    def test_docente_no_puede_acceder_a_me(self):
        docente = get_user_model().objects.create_user("docente", password="clave")
        self.client.force_authenticate(user=docente)

        response = self.client.get("/api/v1/mobile/me/")

        self.assertEqual(response.status_code, 403)
