from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.escuelas.models import Escuela, EscuelaDocente
from apps.escuelas.services import acceso_escuela_service
from apps.escuelas.services.excepciones import EscuelaActivaNoEncontradaError
from apps.usuarios.models import Docente


class AccesoEscuelaTests(TestCase):
    def setUp(self):
        self.escuela = Escuela.objects.create(nombre="Escuela A")
        self.otra_escuela = Escuela.objects.create(nombre="Escuela B")
        self.usuario = get_user_model().objects.create_user("docente", password="clave-segura")
        self.docente = Docente.objects.create(usuario=self.usuario, dni="123")
        EscuelaDocente.objects.create(escuela=self.escuela, docente=self.docente)

    def test_docente_tiene_acceso_solo_a_su_escuela_activa(self):
        self.assertEqual(
            acceso_escuela_service.obtener_escuela_activa_usuario(self.usuario),
            self.escuela,
        )
        self.assertTrue(
            acceso_escuela_service.usuario_tiene_acceso_a_escuela(self.usuario, self.escuela)
        )
        self.assertFalse(
            acceso_escuela_service.usuario_tiene_acceso_a_escuela(self.usuario, self.otra_escuela)
        )

    def test_superadmin_tiene_acceso_global(self):
        superadmin = get_user_model().objects.create_superuser("admin", "admin@example.com", "clave-segura")
        self.assertIsNone(acceso_escuela_service.obtener_escuela_activa_usuario(superadmin))
        self.assertTrue(
            acceso_escuela_service.usuario_tiene_acceso_a_escuela(superadmin, self.otra_escuela)
        )

    def test_usuario_sin_escuela_activa_no_puede_operar(self):
        usuario = get_user_model().objects.create_user("sin-escuela", password="clave-segura")
        Docente.objects.create(usuario=usuario, dni="456")
        with self.assertRaises(EscuelaActivaNoEncontradaError):
            acceso_escuela_service.obtener_escuela_activa_usuario(usuario)
