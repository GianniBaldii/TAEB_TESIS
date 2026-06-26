from importlib import import_module

from django.apps import apps
from django.contrib.messages import ERROR
from django.contrib.messages.storage.base import Message
from django.test import SimpleTestCase
from django.template import Context, Template


class ConfiguracionAlumnosTests(SimpleTestCase):
    def test_app_alumnos_esta_registrada(self):
        configuracion = apps.get_app_config("alumnos")

        self.assertEqual(configuracion.name, "apps.alumnos")
        self.assertEqual(configuracion.verbose_name, "Alumnos")

    def test_paquetes_modulares_pueden_importarse(self):
        self.assertIsNotNone(import_module("apps.alumnos.admin_modulos"))
        self.assertIsNotNone(import_module("apps.alumnos.services"))

    def test_modal_de_errores_se_renderiza_para_error_de_validacion(self):
        contenido = Template(
            '{% include "alumnos/partials/modal_errores_validacion.html" %}'
        ).render(
            Context(
                {
                    "messages": [
                        Message(ERROR, "No se pudo crear el examen", "validation_error")
                    ]
                }
            )
        )

        self.assertIn("No se pudo completar la acción", contenido)
        self.assertIn("No se pudo crear el examen", contenido)
