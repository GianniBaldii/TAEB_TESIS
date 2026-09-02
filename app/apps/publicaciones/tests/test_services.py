from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.escuelas.models import Escuela, EscuelaDocente
from apps.escuelas.services.excepciones import EscuelasError
from apps.publicaciones.models import Publicacion
from apps.publicaciones.services import publicacion_service
from apps.publicaciones.services.excepciones import PublicacionesError
from apps.usuarios.models import Docente


class PublicacionServiceTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("docente", password="clave-segura")
        self.escuela = Escuela.objects.create(nombre="Escuela A")
        self.otra_escuela = Escuela.objects.create(nombre="Escuela B")
        self.docente = Docente.objects.create(usuario=self.usuario, dni="123")
        EscuelaDocente.objects.create(escuela=self.escuela, docente=self.docente)
        self.data_evento = {
            "titulo": "Examen anual",
            "descripcion": "Evaluación de cinturones",
            "tipo_publicacion": Publicacion.Tipo.EVENTO,
            "tematica": Publicacion.Tematica.EXAMENES,
            "fecha_hora_inicio": timezone.now() + timedelta(days=5),
            "fecha_hora_fin": None,
            "ubicacion": "Sede central",
            "cupo_maximo": 30,
        }

    def test_crear_asigna_borrador_escuela_y_autor(self):
        publicacion = publicacion_service.crear_publicacion(
            escuela=self.escuela,
            usuario=self.usuario,
            data=self.data_evento,
        )
        self.assertEqual(publicacion.estado, Publicacion.Estado.BORRADOR)
        self.assertEqual(publicacion.escuela, self.escuela)
        self.assertEqual(publicacion.creado_por, self.usuario)

    def test_docente_no_crea_para_otra_escuela(self):
        with self.assertRaises(EscuelasError):
            publicacion_service.crear_publicacion(
                escuela=self.otra_escuela,
                usuario=self.usuario,
                data=self.data_evento,
            )

    def test_publicar_registra_fecha_publicacion(self):
        publicacion = publicacion_service.crear_publicacion(
            escuela=self.escuela,
            usuario=self.usuario,
            data=self.data_evento,
        )
        publicacion_service.publicar_publicacion(publicacion, usuario=self.usuario)
        self.assertEqual(publicacion.estado, Publicacion.Estado.PUBLICADO)
        self.assertIsNotNone(publicacion.fecha_publicacion)

    def test_anuncio_no_se_puede_cancelar(self):
        anuncio = publicacion_service.crear_publicacion(
            escuela=self.escuela,
            usuario=self.usuario,
            data={
                "titulo": "Novedad",
                "descripcion": "Información institucional",
                "tipo_publicacion": Publicacion.Tipo.ANUNCIO,
                "tematica": Publicacion.Tematica.NOTICIAS,
            },
        )
        publicacion_service.publicar_publicacion(anuncio, usuario=self.usuario)
        with self.assertRaises(PublicacionesError):
            publicacion_service.cancelar_publicacion(anuncio, usuario=self.usuario)

    def test_desactivar_es_baja_logica(self):
        publicacion = publicacion_service.crear_publicacion(
            escuela=self.escuela,
            usuario=self.usuario,
            data=self.data_evento,
        )
        publicacion_service.desactivar_publicacion(publicacion, usuario=self.usuario)
        self.assertFalse(publicacion.activo)
        self.assertTrue(Publicacion.objects.filter(pk=publicacion.pk).exists())
