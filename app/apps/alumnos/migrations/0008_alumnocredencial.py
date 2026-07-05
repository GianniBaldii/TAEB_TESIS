# Generated manually for the mobile MVP.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alumnos", "0007_inscribir_alumnos_escuela_principal"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AlumnoCredencial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "acceso_habilitado",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Indica si el alumno puede iniciar sesion en la "
                            "aplicacion mobile."
                        ),
                    ),
                ),
                (
                    "debe_cambiar_password",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Indica que la contrasena inicial fue creada por "
                            "un docente o superadmin y deberia ser modificada "
                            "por el alumno cuando exista esa funcionalidad."
                        ),
                    ),
                ),
                ("ultimo_login_mobile", models.DateTimeField(blank=True, null=True)),
                ("intentos_fallidos", models.PositiveSmallIntegerField(default=0)),
                ("bloqueado_hasta", models.DateTimeField(blank=True, null=True)),
                (
                    "fecha_ultimo_reset_password",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_modificacion", models.DateTimeField(auto_now=True)),
                (
                    "alumno",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="credencial_mobile",
                        to="alumnos.alumno",
                    ),
                ),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="credencial_alumno",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Credencial mobile de alumno",
                "verbose_name_plural": "Credenciales mobile de alumnos",
            },
        ),
    ]
