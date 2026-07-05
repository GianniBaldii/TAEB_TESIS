from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.alumnos.models import Alumno, AlumnoEscuela
from apps.clases.models import AsistenciaClase, Clase, ClaseAlumno, ClaseHorario, ClaseSesion
from apps.clases.services import asistencia_service, clase_alumno_service, clase_sesion_service
from apps.clases.services.excepciones import ClasesError
from apps.escuelas.models import Escuela, EscuelaDocente
from apps.usuarios.models import Docente


class ClasesServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.usuario = User.objects.create_user("docente", password="clave-segura")
        self.escuela = Escuela.objects.create(nombre="Escuela A")
        self.otra_escuela = Escuela.objects.create(nombre="Escuela B")
        self.docente = Docente.objects.create(usuario=self.usuario, dni="123")
        self.escuela_docente = EscuelaDocente.objects.create(
            escuela=self.escuela,
            docente=self.docente,
        )
        self.clase = Clase.objects.create(
            escuela=self.escuela,
            nombre="Adultos principiantes",
            docente_responsable=self.escuela_docente,
        )
        self.alumno = Alumno.objects.create(nombre="Juan", apellido="Perez", dni="111")
        self.alumno_escuela = AlumnoEscuela.objects.create(
            alumno=self.alumno,
            escuela=self.escuela,
        )
        self.otro_alumno = Alumno.objects.create(nombre="Ana", apellido="Lopez", dni="222")
        self.otro_alumno_escuela = AlumnoEscuela.objects.create(
            alumno=self.otro_alumno,
            escuela=self.otra_escuela,
        )
        self.horario = ClaseHorario.objects.create(
            clase=self.clase,
            dia_semana=ClaseHorario.DiaSemana.MARTES,
            hora_inicio=time(20, 0),
            hora_fin=time(21, 30),
        )

    def test_no_inscribe_alumno_de_otra_escuela(self):
        with self.assertRaises(ClasesError):
            clase_alumno_service.inscribir_alumno_en_clase(
                self.clase,
                self.otro_alumno_escuela,
            )

    def test_inscripcion_inactiva_se_reactiva_sin_duplicar(self):
        inscripcion = clase_alumno_service.inscribir_alumno_en_clase(
            self.clase,
            self.alumno_escuela,
        )
        clase_alumno_service.dar_baja_alumno_de_clase(inscripcion)

        reactivada = clase_alumno_service.inscribir_alumno_en_clase(
            self.clase,
            self.alumno_escuela,
        )

        self.assertEqual(inscripcion.pk, reactivada.pk)
        self.assertEqual(ClaseAlumno.objects.count(), 1)
        self.assertTrue(reactivada.activo)

    def test_crear_o_obtener_sesion_no_duplica(self):
        fecha = date(2026, 7, 7)

        sesion = clase_sesion_service.crear_o_obtener_sesion(
            self.clase,
            self.horario,
            fecha,
        )
        misma_sesion = clase_sesion_service.crear_o_obtener_sesion(
            self.clase,
            self.horario,
            fecha,
        )

        self.assertEqual(sesion.pk, misma_sesion.pk)
        self.assertEqual(ClaseSesion.objects.count(), 1)
        self.assertEqual(sesion.hora_fin, self.horario.hora_fin)

    def test_inicializar_asistencia_crea_pendientes_para_alumnos_activos(self):
        clase_alumno_service.inscribir_alumno_en_clase(self.clase, self.alumno_escuela)
        sesion = clase_sesion_service.crear_o_obtener_sesion(
            self.clase,
            self.horario,
            date(2026, 7, 7),
        )

        asistencia_service.inicializar_asistencias_sesion(sesion, self.usuario)

        asistencia = AsistenciaClase.objects.get()
        self.assertEqual(asistencia.estado, AsistenciaClase.Estado.PENDIENTE)
        self.assertEqual(asistencia.sesion, sesion)

    def test_cerrar_asistencia_convierte_pendientes_en_ausentes(self):
        clase_alumno_service.inscribir_alumno_en_clase(self.clase, self.alumno_escuela)
        sesion = clase_sesion_service.crear_o_obtener_sesion(
            self.clase,
            self.horario,
            date(2026, 7, 7),
        )
        asistencia_service.inicializar_asistencias_sesion(sesion, self.usuario)

        asistencia_service.cerrar_asistencia_sesion(sesion, self.usuario)

        sesion.refresh_from_db()
        asistencia = AsistenciaClase.objects.get()
        self.assertEqual(sesion.estado, ClaseSesion.Estado.FINALIZADA)
        self.assertEqual(asistencia.estado, AsistenciaClase.Estado.AUSENTE)

    def test_sesion_cancelada_no_permite_asistencia(self):
        sesion = clase_sesion_service.crear_o_obtener_sesion(
            self.clase,
            self.horario,
            date(2026, 7, 7),
        )
        clase_sesion_service.cancelar_sesion(sesion, "Feriado")

        with self.assertRaises(ClasesError):
            asistencia_service.inicializar_asistencias_sesion(sesion, self.usuario)
