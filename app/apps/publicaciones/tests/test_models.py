from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.escuelas.models import Escuela
from apps.publicaciones.models import Publicacion


class PublicacionModelTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user("autor", password="clave-segura")
        self.escuela = Escuela.objects.create(nombre="Escuela A")

    def _evento(self, **cambios):
        datos = {
            "escuela": self.escuela,
            "creado_por": self.usuario,
            "titulo": "Torneo provincial",
            "descripcion": "Encuentro deportivo",
            "tipo_publicacion": Publicacion.Tipo.EVENTO,
            "tematica": Publicacion.Tematica.TORNEOS,
            "fecha_hora_inicio": timezone.now() + timedelta(days=2),
        }
        datos.update(cambios)
        return Publicacion(**datos)

    def test_evento_requiere_inicio(self):
        evento = self._evento(fecha_hora_inicio=None)
        with self.assertRaises(ValidationError):
            evento.full_clean()

    def test_finalizacion_debe_ser_posterior_al_inicio(self):
        inicio = timezone.now() + timedelta(days=2)
        evento = self._evento(
            fecha_hora_inicio=inicio,
            fecha_hora_fin=inicio - timedelta(hours=1),
        )
        with self.assertRaises(ValidationError):
            evento.full_clean()

    def test_anuncio_no_admite_cupo(self):
        anuncio = self._evento(
            tipo_publicacion=Publicacion.Tipo.ANUNCIO,
            fecha_hora_inicio=None,
            cupo_maximo=20,
        )
        with self.assertRaises(ValidationError):
            anuncio.full_clean()
