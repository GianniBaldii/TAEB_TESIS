from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardViewTests(TestCase):
    def test_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("core:dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('usuarios:login')}?next={reverse('core:dashboard')}",
        )

    def test_allows_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="tester",
            password="test-password-123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("core:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tablero/inicio.html")
        self.assertContains(response, "Alumnos")
        self.assertContains(response, "No tenés una escuela activa asignada")
        self.assertContains(response, "Clases de hoy")
        self.assertContains(response, "Cobrado este mes")
        self.assertContains(response, "Sin escuela asignada")
        self.assertContains(response, "Asistencias pendientes")
        self.assertNotContains(response, "Administración")

    def test_shows_administration_to_superuser(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            password="test-password-123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("core:dashboard"))

        self.assertContains(response, "Administración")
        self.assertContains(response, "Todas las escuelas")
        self.assertContains(response, "Generar cuotas")
        self.assertContains(response, reverse("admin:index"))
