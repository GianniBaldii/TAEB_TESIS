from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.alumnos.models import Alumno, AlumnoCredencial, AlumnoEscuela
from apps.alumnos.services import alumno_credencial_service
from apps.alumnos.services.excepciones import AlumnosError
from apps.escuelas.models import Escuela, EscuelaDocente
from apps.usuarios.models import Docente


class AlumnoCredencialServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.escuela = Escuela.objects.create(nombre="Escuela A")
        self.otra_escuela = Escuela.objects.create(nombre="Escuela B")
        self.usuario_docente = User.objects.create_user("docente", password="clave")
        self.docente = Docente.objects.create(usuario=self.usuario_docente, dni="999")
        EscuelaDocente.objects.create(escuela=self.escuela, docente=self.docente)
        self.superadmin = User.objects.create_superuser(
            "admin",
            "admin@example.com",
            "clave-segura",
        )
        self.alumno = Alumno.objects.create(
            nombre="Juan",
            apellido="Perez",
            dni="40.123.456",
            activo=True,
        )
        AlumnoEscuela.objects.create(alumno=self.alumno, escuela=self.escuela)

    def test_crear_credencial_genera_usuario_con_dni_normalizado(self):
        credencial = alumno_credencial_service.crear_credencial_mobile_para_alumno(
            alumno=self.alumno,
            password="ClaveSegura123!",
            password_confirmacion="ClaveSegura123!",
            actor=self.usuario_docente,
        )

        self.assertEqual(credencial.usuario.username, "40123456")
        self.assertTrue(credencial.usuario.check_password("ClaveSegura123!"))
        self.assertFalse(hasattr(credencial, "password"))

    def test_no_crea_segunda_credencial_para_mismo_alumno(self):
        alumno_credencial_service.crear_credencial_mobile_para_alumno(
            alumno=self.alumno,
            password="ClaveSegura123!",
            password_confirmacion="ClaveSegura123!",
            actor=self.usuario_docente,
        )

        with self.assertRaises(AlumnosError):
            alumno_credencial_service.crear_credencial_mobile_para_alumno(
                alumno=self.alumno,
                password="OtraClave123!",
                password_confirmacion="OtraClave123!",
                actor=self.usuario_docente,
            )

    def test_no_crea_credencial_sin_inscripcion_activa(self):
        alumno = Alumno.objects.create(nombre="Ana", apellido="Lopez", dni="222")

        with self.assertRaises(AlumnosError):
            alumno_credencial_service.crear_credencial_mobile_para_alumno(
                alumno=alumno,
                password="ClaveSegura123!",
                password_confirmacion="ClaveSegura123!",
                actor=self.superadmin,
            )

    def test_docente_de_otra_escuela_no_puede_generar(self):
        User = get_user_model()
        usuario = User.objects.create_user("docente-b", password="clave")
        docente = Docente.objects.create(usuario=usuario, dni="888")
        EscuelaDocente.objects.create(escuela=self.otra_escuela, docente=docente)

        with self.assertRaises(AlumnosError):
            alumno_credencial_service.crear_credencial_mobile_para_alumno(
                alumno=self.alumno,
                password="ClaveSegura123!",
                password_confirmacion="ClaveSegura123!",
                actor=usuario,
            )

    def test_reset_cambia_password(self):
        credencial = alumno_credencial_service.crear_credencial_mobile_para_alumno(
            alumno=self.alumno,
            password="ClaveSegura123!",
            password_confirmacion="ClaveSegura123!",
            actor=self.superadmin,
        )

        alumno_credencial_service.resetear_password_credencial_mobile(
            credencial=credencial,
            password="NuevaClave123!",
            password_confirmacion="NuevaClave123!",
            actor=self.superadmin,
        )

        credencial.usuario.refresh_from_db()
        credencial.refresh_from_db()
        self.assertTrue(credencial.usuario.check_password("NuevaClave123!"))
        self.assertTrue(credencial.debe_cambiar_password)
        self.assertIsNotNone(credencial.fecha_ultimo_reset_password)

    def test_bloquear_y_reactivar_acceso(self):
        credencial = alumno_credencial_service.crear_credencial_mobile_para_alumno(
            alumno=self.alumno,
            password="ClaveSegura123!",
            password_confirmacion="ClaveSegura123!",
            actor=self.superadmin,
        )

        alumno_credencial_service.bloquear_acceso_mobile(
            credencial=credencial,
            actor=self.superadmin,
        )
        credencial.refresh_from_db()
        self.assertFalse(credencial.acceso_habilitado)

        alumno_credencial_service.reactivar_acceso_mobile(
            credencial=credencial,
            actor=self.superadmin,
        )
        credencial.refresh_from_db()
        self.assertTrue(credencial.acceso_habilitado)
