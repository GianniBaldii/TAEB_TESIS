from datetime import date, timedelta

from django.template import Context, Template
from django.test import TestCase

from apps.alumnos.constants.progreso_taekwondo import EstadoHabilitacion
from apps.alumnos.models import (
    Alumno,
    AlumnoCinturonHistorial,
    Cinturon,
    Examen,
    ExamenTemplate,
)
from apps.alumnos.services import trayectoria_taekwondista_service as service


class TrayectoriaTaekwondistaServiceTests(TestCase):
    def setUp(self):
        self.blanco = Cinturon.objects.create(
            nombre="Blanco", color="blanco", tipo_rango="GUP", numeracion=10, orden=1
        )
        self.punta_amarilla = Cinturon.objects.create(
            nombre="Punta Amarilla",
            color="blanco/amarillo",
            tipo_rango="GUP",
            numeracion=9,
            orden=2,
        )
        self.amarillo = Cinturon.objects.create(
            nombre="Amarillo", color="amarillo", tipo_rango="GUP", numeracion=8, orden=3
        )
        self.punta_negra = Cinturon.objects.create(
            nombre="Punta Negra",
            color="rojo/negro",
            tipo_rango="GUP",
            numeracion=1,
            orden=10,
        )
        self.primer_dan = Cinturon.objects.create(
            nombre="1° Dan", color="negro", tipo_rango="DAN", numeracion=1, orden=11
        )
        self.alumno = Alumno.objects.create(
            nombre="Ada",
            apellido="Lovelace",
            dni="1",
            cinturon_actual=self.blanco,
            fecha_inicio_taekwondo=date(2026, 1, 1),
        )

    def _template(self, cinturon):
        return ExamenTemplate.objects.create(cinturon=cinturon, nombre=f"Template {cinturon.nombre}")

    def _examen(self, destino, fecha, estado=Examen.Estado.APROBADO):
        return Examen.objects.create(
            alumno=self.alumno,
            examen_template=self._template(destino),
            cinturon_origen=self.blanco,
            cinturon_destino=destino,
            fecha_examen=fecha,
            estado=estado,
        )

    def _historial(self, cinturon, fecha):
        return AlumnoCinturonHistorial.objects.create(
            alumno=self.alumno,
            cinturon=cinturon,
            fecha_obtencion=fecha,
            examen=self._examen(cinturon, fecha),
        )

    def test_calcula_tiempo_desde_ultimo_cinturon_usando_fecha_inicio_si_no_hay_historial(self):
        dias = service.obtener_dias_desde_ultimo_cinturon(
            self.alumno, fecha_referencia=date(2026, 2, 1)
        )
        self.assertEqual(dias, 31)

    def test_obtiene_tiempo_orientativo_segun_cinturon_actual(self):
        tiempo = service.obtener_tiempo_orientativo_para_siguiente_examen(self.blanco)
        self.assertEqual(tiempo.meses_minimos, 3)
        self.assertEqual(tiempo.descripcion, "3 meses")

    def test_estado_recien_promovido(self):
        self._historial(self.blanco, date(2026, 3, 1))
        estado = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 3, 20)
        )
        self.assertEqual(estado["codigo"], EstadoHabilitacion.RECIEN_PROMOVIDO)

    def test_estado_aun_no_habilitado(self):
        self._historial(self.blanco, date(2026, 1, 1))
        estado = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 2, 15)
        )
        self.assertEqual(estado["codigo"], EstadoHabilitacion.AUN_NO_HABILITADO)

    def test_estado_proximo_a_habilitarse(self):
        self._historial(self.blanco, date(2026, 1, 1))
        estado = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 3, 20)
        )
        self.assertEqual(estado["codigo"], EstadoHabilitacion.PROXIMO_A_HABILITARSE)

    def test_estado_habilitado_orientativamente(self):
        self._historial(self.blanco, date(2026, 1, 1))
        estado = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 4, 5)
        )
        self.assertEqual(estado["codigo"], EstadoHabilitacion.HABILITADO_ORIENTATIVAMENTE)

    def test_estado_tiempo_excedido(self):
        self._historial(self.blanco, date(2026, 1, 1))
        estado = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 6, 20)
        )
        self.assertEqual(estado["codigo"], EstadoHabilitacion.TIEMPO_EXCEDIDO)

    def test_manejo_especial_primer_gup_a_primer_dan(self):
        self.alumno.cinturon_actual = self.punta_negra
        self.alumno.save(update_fields=["cinturon_actual"])
        self._historial(self.punta_negra, date(2026, 1, 1))

        antes_de_ventana = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 5, 1)
        )
        dentro_de_ventana = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 8, 1)
        )
        final_de_ventana = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2026, 12, 1)
        )
        excedido = service.obtener_estado_habilitacion_rendir(
            self.alumno, fecha_referencia=date(2027, 2, 1)
        )

        self.assertEqual(antes_de_ventana["codigo"], EstadoHabilitacion.AUN_NO_HABILITADO)
        self.assertEqual(dentro_de_ventana["codigo"], EstadoHabilitacion.HABILITADO_ORIENTATIVAMENTE)
        self.assertEqual(final_de_ventana["codigo"], EstadoHabilitacion.HABILITADO_ORIENTATIVAMENTE)
        self.assertEqual(excedido["codigo"], EstadoHabilitacion.TIEMPO_EXCEDIDO)

    def test_promedio_historico_basico(self):
        self._historial(self.blanco, date(2026, 1, 1))
        self._historial(self.punta_amarilla, date(2026, 4, 1))
        self._historial(self.amarillo, date(2026, 7, 1))

        promedio = service.obtener_promedio_historico_promociones(self.alumno)

        self.assertEqual(promedio, 91)

    def test_analisis_sin_historial_genera_timeline_vacio_y_glosario(self):
        analisis = service.obtener_analisis_trayectoria(
            self.alumno, fecha_referencia=date(2026, 1, 20)
        )

        self.assertEqual(analisis["timeline_historial"], [])
        self.assertGreaterEqual(len(analisis["glosario_tiempos"]), 10)

    def test_timeline_calcula_intervalos_y_acumulados(self):
        self._historial(self.blanco, date(2026, 1, 1))
        self._historial(self.punta_amarilla, date(2026, 4, 1))

        timeline = service.construir_timeline_historial(self.alumno)

        self.assertEqual(len(timeline), 2)
        self.assertTrue(timeline[0]["es_primero"])
        self.assertEqual(timeline[1]["tiempo_desde_anterior_dias"], 90)

    def test_render_glosario_y_timeline_sin_datos(self):
        analisis = service.obtener_analisis_trayectoria(
            self.alumno, fecha_referencia=date.today()
        )
        html = Template(
            """
            {% include "alumnos/partials/progreso/glosario_tiempos.html" %}
            {% include "alumnos/partials/historial/timeline_historial_cinturones.html" %}
            """
        ).render(Context({"analisis_trayectoria": analisis, "alumno": self.alumno}))

        self.assertIn("Referencia orientativa", html)
        self.assertIn("Sin historial registrado todavía", html)
