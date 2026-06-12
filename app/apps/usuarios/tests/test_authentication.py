from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin-taeb",
            password="test-password-123",
        )

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("usuarios:login"),
            {
                "username": self.user.username,
                "password": "test-password-123",
            },
        )

        self.assertRedirects(response, reverse("core:dashboard"))

    def test_logout_ends_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("usuarios:logout"))

        self.assertRedirects(response, reverse("usuarios:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
