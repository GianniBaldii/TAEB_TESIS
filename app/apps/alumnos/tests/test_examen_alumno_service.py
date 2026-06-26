from datetime import date

from django.test import TestCase

from apps.alumnos.models import Alumno, Cinturon, Examen, ExamenDetalle, ExamenTemplate, ExamenTemplateItem, ExamenTemplateSeccion
from apps.alumnos.services import alumno_service
from apps.alumnos.services.examen_alumno_service import (
    CONCEPTOS_GUP_VALIDOS,
    actualizar_evaluaciones_examen,
    crear_examen_para_alumno,
)
from apps.alumnos.services.excepciones import AlumnosError


class ExamenAlumnoServiceTests(TestCase):
    def setUp(self):
        self.blanco = Cinturon.objects.create(nombre="Blanco", color="blanco", tipo_rango="GUP", numeracion=10, orden=1)
        self.amarillo = Cinturon.objects.create(nombre="Amarillo", color="amarillo", tipo_rango="GUP", numeracion=9, orden=2)
        self.dan = Cinturon.objects.create(nombre="Dan", color="negro", tipo_rango="DAN", numeracion=1, orden=3)
        self.alumno = Alumno.objects.create(nombre="Ada", apellido="Lovelace", dni="1", cinturon_actual=self.blanco)
        self._template(self.amarillo)
        self._template(self.dan)

    def _template(self, cinturon):
        return ExamenTemplate.objects.create(cinturon=cinturon, nombre=f"Template {cinturon.nombre}")

    def _examen(self, destino, estado=Examen.Estado.PENDIENTE, historico=False):
        return Examen.objects.create(alumno=self.alumno, examen_template=self._template(destino), cinturon_origen=self.blanco, cinturon_destino=destino, fecha_examen=date.today(), estado=estado, es_historico=historico)

    def test_no_permite_dos_examenes_actuales_pendientes(self):
        crear_examen_para_alumno(self.alumno, date.today())
        with self.assertRaises(AlumnosError):
            crear_examen_para_alumno(self.alumno, date.today())

    def test_crear_alumno_asigna_el_cinturon_inicial_si_no_se_indica_otro(self):
        alumno = alumno_service.crear_alumno(
            {
                "nombre": "Grace",
                "apellido": "Hopper",
                "dni": "2",
                "fecha_inicio_taekwondo": date.today(),
            }
        )
        self.assertEqual(alumno.cinturon_actual, self.blanco)

    def test_no_permite_rendir_cinturon_ya_aprobado(self):
        self._examen(self.amarillo, Examen.Estado.APROBADO)
        with self.assertRaises(AlumnosError):
            crear_examen_para_alumno(self.alumno, date.today())

    def test_permite_rendir_luego_de_desaprobado(self):
        self._examen(self.amarillo, Examen.Estado.DESAPROBADO)
        examen = crear_examen_para_alumno(self.alumno, date.today())
        self.assertEqual(examen.cinturon_destino, self.amarillo)

    def test_examen_actual_calcula_origen_y_destino(self):
        examen = crear_examen_para_alumno(self.alumno, date.today())
        self.assertEqual(examen.cinturon_origen, self.blanco)
        self.assertEqual(examen.cinturon_destino, self.amarillo)

    def test_examen_historico_calcula_origen(self):
        examen = crear_examen_para_alumno(self.alumno, date.today(), cinturon_destino=self.amarillo, es_historico=True)
        self.assertEqual(examen.cinturon_origen, self.blanco)
        self.assertTrue(examen.es_historico)

    def test_no_permite_usar_el_cinturon_inicial_como_destino_historico(self):
        with self.assertRaises(AlumnosError):
            crear_examen_para_alumno(
                self.alumno,
                date.today(),
                cinturon_destino=self.blanco,
                es_historico=True,
            )

    def test_no_permite_historico_para_cinturon_ya_aprobado(self):
        self._examen(self.amarillo, Examen.Estado.APROBADO)
        with self.assertRaises(AlumnosError):
            crear_examen_para_alumno(
                self.alumno,
                date.today(),
                cinturon_destino=self.amarillo,
                es_historico=True,
            )

    def test_no_permite_duplicar_examen_historico_en_la_misma_fecha(self):
        crear_examen_para_alumno(self.alumno, date.today(), cinturon_destino=self.amarillo, es_historico=True)
        with self.assertRaises(AlumnosError):
            crear_examen_para_alumno(self.alumno, date.today(), cinturon_destino=self.amarillo, es_historico=True)

    def test_conceptos_gup_validos_y_no_validos(self):
        examen = crear_examen_para_alumno(self.alumno, date.today())
        seccion = ExamenTemplateSeccion.objects.create(examen_template=examen.examen_template, nombre="General")
        item = ExamenTemplateItem.objects.create(seccion=seccion, nombre="Concepto", tipo_evaluacion="CONCEPTO")
        detalle = ExamenDetalle.objects.create(examen=examen, template_item=item)
        actualizar_evaluaciones_examen(examen, {"detalles": {detalle.pk: {"concepto": CONCEPTOS_GUP_VALIDOS[0]}}})
        detalle.refresh_from_db()
        self.assertEqual(detalle.concepto, CONCEPTOS_GUP_VALIDOS[0])
        with self.assertRaises(AlumnosError):
            actualizar_evaluaciones_examen(examen, {"detalles": {detalle.pk: {"concepto": "LIBRE"}}})

    def test_concepto_dan_permite_texto_libre(self):
        examen = self._examen(self.dan)
        seccion = ExamenTemplateSeccion.objects.create(examen_template=examen.examen_template, nombre="Dan")
        item = ExamenTemplateItem.objects.create(seccion=seccion, nombre="Concepto", tipo_evaluacion="CONCEPTO")
        detalle = ExamenDetalle.objects.create(examen=examen, template_item=item)
        actualizar_evaluaciones_examen(examen, {"detalles": {detalle.pk: {"concepto": "Escala propia"}}})
        detalle.refresh_from_db()
        self.assertEqual(detalle.concepto, "Escala propia")
