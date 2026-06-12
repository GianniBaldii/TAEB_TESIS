from importlib import import_module

from django.apps import apps
from django.test import SimpleTestCase


class ConfiguracionAlumnosTests(SimpleTestCase):
    def test_app_alumnos_esta_registrada(self):
        configuracion = apps.get_app_config("alumnos")

        self.assertEqual(configuracion.name, "apps.alumnos")
        self.assertEqual(configuracion.verbose_name, "Alumnos")

    def test_paquetes_modulares_pueden_importarse(self):
        self.assertIsNotNone(import_module("apps.alumnos.admin_modulos"))
        self.assertIsNotNone(import_module("apps.alumnos.services"))
