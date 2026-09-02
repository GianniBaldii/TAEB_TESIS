import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("escuelas", "0002_alter_escueladocente_docente_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Publicacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=180)),
                ("descripcion", models.TextField()),
                ("tipo_publicacion", models.CharField(choices=[("ANUNCIO", "Anuncio"), ("EVENTO", "Evento")], max_length=10)),
                ("tematica", models.CharField(choices=[("NOTICIAS", "Noticias"), ("BENEFICIOS", "Beneficios"), ("EXAMENES", "Exámenes"), ("TORNEOS", "Torneos")], max_length=12)),
                ("fecha_hora_inicio", models.DateTimeField(blank=True, null=True)),
                ("fecha_hora_fin", models.DateTimeField(blank=True, null=True)),
                ("ubicacion", models.CharField(blank=True, max_length=255, null=True)),
                ("cupo_maximo", models.PositiveIntegerField(blank=True, null=True)),
                ("estado", models.CharField(choices=[("BORRADOR", "Borrador"), ("PUBLICADO", "Publicado"), ("CANCELADO", "Cancelado"), ("FINALIZADO", "Finalizado")], default="BORRADOR", max_length=12)),
                ("activo", models.BooleanField(default=True)),
                ("fecha_publicacion", models.DateTimeField(blank=True, null=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_modificacion", models.DateTimeField(auto_now=True)),
                ("creado_por", models.ForeignKey(db_column="id_creado_por", on_delete=django.db.models.deletion.PROTECT, related_name="publicaciones_creadas", to=settings.AUTH_USER_MODEL)),
                ("escuela", models.ForeignKey(db_column="id_escuela", on_delete=django.db.models.deletion.PROTECT, related_name="publicaciones", to="escuelas.escuela")),
            ],
            options={
                "verbose_name": "Publicación",
                "verbose_name_plural": "Publicaciones",
                "db_table": "publicaciones",
                "ordering": ["-fecha_creacion"],
            },
        ),
    ]
