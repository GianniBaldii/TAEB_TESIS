from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.escuelas.models import Escuela, EscuelaDocente
from apps.publicaciones.models import Publicacion
from apps.usuarios.models import Docente


class PublicacionViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.usuario = User.objects.create_user("docente", password="clave-segura")
        self.otro_usuario = User.objects.create_user("otro", password="clave-segura")
        self.escuela = Escuela.objects.create(nombre="Escuela A")
        self.otra_escuela = Escuela.objects.create(nombre="Escuela B")
        docente = Docente.objects.create(usuario=self.usuario, dni="123")
        otro_docente = Docente.objects.create(usuario=self.otro_usuario, dni="456")
        EscuelaDocente.objects.create(escuela=self.escuela, docente=docente)
        EscuelaDocente.objects.create(escuela=self.otra_escuela, docente=otro_docente)
        self.publicacion = Publicacion.objects.create(
            escuela=self.escuela,
            creado_por=self.usuario,
            titulo="Evento propio",
            descripcion="Descripción",
            tipo_publicacion=Publicacion.Tipo.EVENTO,
            tematica=Publicacion.Tematica.TORNEOS,
            fecha_hora_inicio=timezone.now() + timedelta(days=3),
        )
        self.ajena = Publicacion.objects.create(
            escuela=self.otra_escuela,
            creado_por=self.otro_usuario,
            titulo="Evento ajeno",
            descripcion="Descripción",
            tipo_publicacion=Publicacion.Tipo.EVENTO,
            tematica=Publicacion.Tematica.TORNEOS,
            fecha_hora_inicio=timezone.now() + timedelta(days=3),
        )
        self.client.force_login(self.usuario)

    def test_listado_muestra_solo_publicaciones_de_su_escuela(self):
        response = self.client.get(reverse("publicaciones:publicacion_list"))
        self.assertContains(response, "Evento propio")
        self.assertNotContains(response, "Evento ajeno")

    def test_detalle_ajeno_devuelve_404(self):
        response = self.client.get(
            reverse("publicaciones:publicacion_detail", args=[self.ajena.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_publicar_por_get_no_cambia_estado(self):
        response = self.client.get(
            reverse("publicaciones:publicacion_publicar", args=[self.publicacion.pk])
        )
        self.assertEqual(response.status_code, 405)
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.estado, Publicacion.Estado.BORRADOR)

    def test_publicar_por_post_cambia_estado(self):
        self.client.post(
            reverse("publicaciones:publicacion_publicar", args=[self.publicacion.pk])
        )
        self.publicacion.refresh_from_db()
        self.assertEqual(self.publicacion.estado, Publicacion.Estado.PUBLICADO)

    def test_usuario_no_autenticado_es_redirigido(self):
        self.client.logout()
        response = self.client.get(reverse("publicaciones:publicacion_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("usuarios:login"), response.url)
