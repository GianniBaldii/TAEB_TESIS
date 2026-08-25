from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.alumnos.models import Alumno, AlumnoEscuela, Cinturon
from apps.escuelas.models import Escuela


class AlumnoDetailViewTests(TestCase):
    def test_superusuario_puede_ver_ficha_con_inscripcion_inactiva(self):
        usuario = get_user_model().objects.create_superuser(
            username="admin-ficha-inactiva",
            password="test-password-123",
        )
        escuela = Escuela.objects.create(nombre="Escuela ficha inactiva")
        alumno = Alumno.objects.create(
            nombre="Alumno",
            apellido="Inactivo",
            dni="99000001",
            cinturon_actual=Cinturon.objects.order_by("orden").first(),
        )
        AlumnoEscuela.objects.create(
            alumno=alumno,
            escuela=escuela,
            activo=False,
        )
        self.client.force_login(usuario)

        response = self.client.get(
            reverse("alumnos:alumno_detail", kwargs={"pk": alumno.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "alumnos/alumno_detail.html")
        self.assertContains(response, "Inactivo")
        self.assertFalse(response.context["inscripcion"].activo)
