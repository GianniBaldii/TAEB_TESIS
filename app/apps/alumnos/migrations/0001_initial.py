from django.db import migrations, models
import django.db.models.deletion


CINTURONES_INICIALES = [
    (1, "Blanco", "Blanco", "GUP", 10),
    (2, "Blanco punta amarilla", "Blanco punta amarilla", "GUP", 9),
    (3, "Amarillo", "Amarillo", "GUP", 8),
    (4, "Amarillo punta verde", "Amarillo punta verde", "GUP", 7),
    (5, "Verde", "Verde", "GUP", 6),
    (6, "Verde punta azul", "Verde punta azul", "GUP", 5),
    (7, "Azul", "Azul", "GUP", 4),
    (8, "Azul punta roja", "Azul punta roja", "GUP", 3),
    (9, "Rojo", "Rojo", "GUP", 2),
    (10, "Rojo punta negra", "Rojo punta negra", "GUP", 1),
    (11, "Negro I Dan", "Negro", "DAN", 1),
    (12, "Negro II Dan", "Negro", "DAN", 2),
    (13, "Negro III Dan", "Negro", "DAN", 3),
    (14, "Negro IV Dan", "Negro", "DAN", 4),
    (15, "Negro V Dan", "Negro", "DAN", 5),
    (16, "Negro VI Dan", "Negro", "DAN", 6),
    (17, "Negro VII Dan", "Negro", "DAN", 7),
    (18, "Negro VIII Dan", "Negro", "DAN", 8),
    (19, "Negro IX Dan", "Negro", "DAN", 9),
]


def crear_cinturones(apps, schema_editor):
    Cinturon = apps.get_model("alumnos", "Cinturon")
    for orden, nombre, color, tipo_rango, numeracion in CINTURONES_INICIALES:
        Cinturon.objects.update_or_create(
            orden=orden,
            defaults={
                "nombre": nombre,
                "color": color,
                "tipo_rango": tipo_rango,
                "numeracion": numeracion,
                "activo": True,
            },
        )


def eliminar_cinturones(apps, schema_editor):
    Cinturon = apps.get_model("alumnos", "Cinturon")
    Cinturon.objects.filter(orden__in=[item[0] for item in CINTURONES_INICIALES]).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Alumno",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100)),
                ("apellido", models.CharField(max_length=100)),
                ("dni", models.CharField(max_length=20, unique=True)),
                ("fecha_nacimiento", models.DateField(blank=True, null=True)),
                ("email", models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ("telefono", models.CharField(blank=True, max_length=30, null=True)),
                ("direccion", models.CharField(blank=True, max_length=255, null=True)),
                ("peso_aproximado", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("altura_aproximada", models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ("activo", models.BooleanField(default=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_modificacion", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Alumno",
                "verbose_name_plural": "Alumnos",
                "ordering": ["apellido", "nombre"],
            },
        ),
        migrations.CreateModel(
            name="Cinturon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100)),
                ("color", models.CharField(max_length=80)),
                ("tipo_rango", models.CharField(choices=[("GUP", "GUP"), ("DAN", "DAN")], max_length=3)),
                ("numeracion", models.PositiveSmallIntegerField()),
                ("orden", models.PositiveSmallIntegerField(unique=True)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Cinturon",
                "verbose_name_plural": "Cinturones",
                "ordering": ["orden"],
            },
        ),
        migrations.CreateModel(
            name="ExamenTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=150)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("nota_minima_aprobacion", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("version", models.PositiveSmallIntegerField(default=1)),
                ("activo", models.BooleanField(default=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_modificacion", models.DateTimeField(auto_now=True)),
                ("cinturon", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="templates_examen", to="alumnos.cinturon")),
            ],
            options={
                "verbose_name": "Template de examen",
                "verbose_name_plural": "Templates de examenes",
                "ordering": ["cinturon__orden", "nombre", "-version"],
            },
        ),
        migrations.CreateModel(
            name="ExamenTemplateSeccion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("orden", models.PositiveSmallIntegerField(default=1)),
                ("obligatorio", models.BooleanField(default=True)),
                ("activo", models.BooleanField(default=True)),
                ("examen_template", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="secciones", to="alumnos.examentemplate")),
            ],
            options={
                "verbose_name": "Seccion de template",
                "verbose_name_plural": "Secciones de template",
                "ordering": ["orden"],
            },
        ),
        migrations.CreateModel(
            name="ExamenTemplateItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=150)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("tipo_evaluacion", models.CharField(choices=[("NUMERICA", "Numerica"), ("CONCEPTO", "Concepto"), ("TEXTO", "Texto"), ("CHECK", "Check")], max_length=10)),
                ("orden", models.PositiveSmallIntegerField(default=1)),
                ("puntaje_maximo", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("ponderacion", models.DecimalField(decimal_places=2, default=1, max_digits=5)),
                ("obligatorio", models.BooleanField(default=True)),
                ("activo", models.BooleanField(default=True)),
                ("seccion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="alumnos.examentemplateseccion")),
            ],
            options={
                "verbose_name": "Item de template",
                "verbose_name_plural": "Items de template",
                "ordering": ["seccion__orden", "orden"],
            },
        ),
        migrations.CreateModel(
            name="Examen",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_examen", models.DateField()),
                ("lugar", models.CharField(blank=True, max_length=150, null=True)),
                ("estado", models.CharField(choices=[("PENDIENTE", "Pendiente"), ("APROBADO", "Aprobado"), ("DESAPROBADO", "Desaprobado"), ("AUSENTE", "Ausente"), ("ANULADO", "Anulado")], default="PENDIENTE", max_length=12)),
                ("nota_final", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("resultado_final", models.CharField(blank=True, max_length=20, null=True)),
                ("observaciones", models.TextField(blank=True, null=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_modificacion", models.DateTimeField(auto_now=True)),
                ("alumno", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="examenes", to="alumnos.alumno")),
                ("cinturon_destino", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="examenes_destino", to="alumnos.cinturon")),
                ("cinturon_origen", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="examenes_origen", to="alumnos.cinturon")),
                ("examen_template", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="examenes", to="alumnos.examentemplate")),
            ],
            options={
                "verbose_name": "Examen",
                "verbose_name_plural": "Examenes",
                "ordering": ["-fecha_examen", "-fecha_creacion"],
            },
        ),
        migrations.CreateModel(
            name="AlumnoCinturonHistorial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_obtencion", models.DateField()),
                ("observaciones", models.TextField(blank=True, null=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("alumno", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="historial_cinturones", to="alumnos.alumno")),
                ("cinturon", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="historial_alumnos", to="alumnos.cinturon")),
                ("examen", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="historial_cinturon", to="alumnos.examen")),
            ],
            options={
                "verbose_name": "Historial de cinturon",
                "verbose_name_plural": "Historiales de cinturones",
                "ordering": ["fecha_obtencion", "cinturon__orden"],
            },
        ),
        migrations.CreateModel(
            name="ExamenDetalle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nota_numerica", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("concepto", models.CharField(blank=True, max_length=50, null=True)),
                ("valor_texto", models.TextField(blank=True, null=True)),
                ("aprobado", models.BooleanField(blank=True, null=True)),
                ("observaciones", models.TextField(blank=True, null=True)),
                ("examen", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="detalles", to="alumnos.examen")),
                ("template_item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="detalles_examen", to="alumnos.examentemplateitem")),
            ],
            options={
                "verbose_name": "Detalle de examen",
                "verbose_name_plural": "Detalles de examen",
                "ordering": ["template_item__seccion__orden", "template_item__orden"],
            },
        ),
        migrations.AddField(
            model_name="alumno",
            name="cinturon_actual",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="alumnos_actuales", to="alumnos.cinturon"),
        ),
        migrations.AddConstraint(
            model_name="cinturon",
            constraint=models.UniqueConstraint(fields=("tipo_rango", "numeracion"), name="cinturon_tipo_rango_numeracion_unicos"),
        ),
        migrations.AddConstraint(
            model_name="examentemplateseccion",
            constraint=models.UniqueConstraint(fields=("examen_template", "nombre"), name="seccion_template_nombre_unicos"),
        ),
        migrations.AddConstraint(
            model_name="alumnocinturonhistorial",
            constraint=models.UniqueConstraint(fields=("alumno", "cinturon"), name="historial_alumno_cinturon_unicos"),
        ),
        migrations.AddConstraint(
            model_name="examendetalle",
            constraint=models.UniqueConstraint(fields=("examen", "template_item"), name="detalle_examen_template_item_unicos"),
        ),
        migrations.RunPython(crear_cinturones, eliminar_cinturones),
    ]
