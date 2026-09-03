from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.usuarios.models import Docente


class ResetearCredencialesDocenteTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin-credenciales", password="Admin-test-123"
        )
        self.usuario_docente = get_user_model().objects.create_user(
            username="docente-credenciales", password="Clave-anterior-123"
        )
        self.docente = Docente.objects.create(
            usuario=self.usuario_docente, dni="DOC-RESET-1"
        )
        self.url = reverse(
            "escuelas:docente_resetear_password", args=[self.docente.pk]
        )

    def test_superadmin_puede_resetear_password(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.url,
            {"password1": "Nueva-clave-segura-456", "password2": "Nueva-clave-segura-456"},
        )

        self.assertRedirects(
            response, reverse("escuelas:docente_detail", args=[self.docente.pk])
        )
        self.usuario_docente.refresh_from_db()
        self.assertTrue(self.usuario_docente.check_password("Nueva-clave-segura-456"))

    def test_passwords_distintos_no_modifican_credencial(self):
        self.client.force_login(self.admin)

        self.client.post(
            self.url,
            {"password1": "Nueva-clave-segura-456", "password2": "Otra-clave-segura-789"},
        )

        self.usuario_docente.refresh_from_db()
        self.assertTrue(self.usuario_docente.check_password("Clave-anterior-123"))

    def test_usuario_no_admin_no_puede_resetear_password(self):
        self.client.force_login(self.usuario_docente)

        response = self.client.post(
            self.url,
            {"password1": "Nueva-clave-segura-456", "password2": "Nueva-clave-segura-456"},
        )

        self.assertEqual(response.status_code, 403)
        self.usuario_docente.refresh_from_db()
        self.assertTrue(self.usuario_docente.check_password("Clave-anterior-123"))
