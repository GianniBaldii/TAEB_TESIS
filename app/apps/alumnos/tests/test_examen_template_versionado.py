from datetime import date

from django.test import TestCase

from apps.alumnos.models import (
    Alumno,
    Cinturon,
    Examen,
    ExamenTemplate,
    ExamenTemplateItem,
    ExamenTemplateSeccion,
)
from apps.alumnos.services import examen_template_service
from apps.alumnos.services.excepciones import AlumnosError


class ExamenTemplateVersionadoTests(TestCase):
    def setUp(self):
        self.cinturon = Cinturon.objects.create(
            nombre="Amarillo", color="amarillo", tipo_rango="GUP", numeracion=9, orden=2
        )
        self.template = ExamenTemplate.objects.create(
            cinturon=self.cinturon,
            nombre="GUP base",
            descripcion="Criterios iniciales",
            nota_minima_aprobacion=6,
            activo=True,
        )
        self.seccion = ExamenTemplateSeccion.objects.create(
            examen_template=self.template, nombre="Tecnica", orden=1
        )
        self.item = ExamenTemplateItem.objects.create(
            seccion=self.seccion,
            nombre="Poomsae",
            tipo_evaluacion=ExamenTemplateItem.TipoEvaluacion.CONCEPTO,
            orden=1,
        )

    def _crear_examen(self):
        alumno = Alumno.objects.create(nombre="Ada", apellido="Lovelace", dni="100")
        return Examen.objects.create(
            alumno=alumno,
            examen_template=self.template,
            cinturon_origen=self.cinturon,
            cinturon_destino=self.cinturon,
            fecha_examen=date.today(),
        )

    def test_template_usado_no_puede_modificarse(self):
        self._crear_examen()
        with self.assertRaises(AlumnosError):
            examen_template_service.actualizar_template(
                self.template, {"nombre": "Criterios modificados"}
            )

    def test_duplicar_copia_secciones_e_items_e_incrementa_version(self):
        nuevo = examen_template_service.duplicar_template(self.template)

        self.assertEqual(nuevo.version, 2)
        self.assertEqual(nuevo.template_origen, self.template)
        self.assertFalse(nuevo.activo)
        nueva_seccion = nuevo.secciones.get()
        nuevo_item = nueva_seccion.items.get()
        self.assertEqual(nueva_seccion.nombre, self.seccion.nombre)
        self.assertEqual(nuevo_item.nombre, self.item.nombre)
        self.assertEqual(nuevo_item.tipo_evaluacion, self.item.tipo_evaluacion)

    def test_activar_nueva_version_desactiva_la_anterior(self):
        nuevo = examen_template_service.duplicar_template(self.template)
        examen_template_service.activar_template(nuevo)

        self.template.refresh_from_db()
        nuevo.refresh_from_db()
        self.assertFalse(self.template.activo)
        self.assertTrue(nuevo.activo)

    def test_examen_historico_conserva_template_original(self):
        examen = self._crear_examen()
        nuevo = examen_template_service.duplicar_template(self.template)

        examen.refresh_from_db()
        self.assertEqual(examen.examen_template, self.template)
        self.assertNotEqual(examen.examen_template, nuevo)

    def test_elimina_template_sin_examenes(self):
        template_id = self.template.pk
        examen_template_service.eliminar_template(self.template)

        self.assertFalse(ExamenTemplate.objects.filter(pk=template_id).exists())

    def test_no_elimina_template_usado(self):
        self._crear_examen()
        with self.assertRaises(AlumnosError):
            examen_template_service.eliminar_template(self.template)
