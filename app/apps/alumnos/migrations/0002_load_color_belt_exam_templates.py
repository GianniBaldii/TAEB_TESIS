from django.db import migrations


DESCRIPCION_TEMPLATE = (
    "Template inicial basado en planilla de examen de libreta."
)

SECCIONES_ORDEN = [
    "Ejercicios fundamentales",
    "Tul",
    "Sambo Matsokgi",
    "Ibo Matsokgi",
    "Ilbo Matsokgi",
    "T\u00e9cnicas de patadas",
    "Jayu Matsokgi",
    "Hosin Sool",
    "Rotura",
    "Teor\u00eda",
    "Actitud",
]

TEMPLATES_GUP = [
    {
        "numeracion": 9,
        "nombre": "Examen 9\u00b0 GUP - Cintur\u00f3n Blanco punta amarilla",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Saju-Jirugi", "Saju-Makgi"],
            "Sambo Matsokgi": ["Sin oponente", "1 sentido"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["Ilbo Matsokgi"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["Rotura"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 8,
        "nombre": "Examen 8\u00b0 GUP - Cintur\u00f3n Amarillo",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Saju-Jirugi / Saju-Makgi", "Chon-Ji"],
            "Sambo Matsokgi": ["Sin oponente", "1 sentido"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["Ilbo Matsokgi"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["Rotura"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 7,
        "nombre": "Examen 7\u00b0 GUP - Cintur\u00f3n Amarillo punta verde",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Chon-Ji", "Dan-Gun"],
            "Sambo Matsokgi": ["Sambo Matsokgi"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["Ilbo Matsokgi"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["Rotura"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 6,
        "nombre": "Examen 6\u00b0 GUP - Cintur\u00f3n Verde",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Dan-Gun", "Do-San"],
            "Sambo Matsokgi": ["Sambo Matsokgi"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["Ilbo Matsokgi"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["Rotura"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 5,
        "nombre": "Examen 5\u00b0 GUP - Cintur\u00f3n Verde punta azul",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Do-San", "Won-Hyo"],
            "Sambo Matsokgi": ["Sambo Matsokgi"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["Ilbo Matsokgi"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto y/o giro"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["Rotura"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 4,
        "nombre": "Examen 4\u00b0 GUP - Cintur\u00f3n Azul",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Won-Hyo", "Yul-Gok"],
            "Sambo Matsokgi": ["Sambo Matsokgi"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["Ilbo Matsokgi"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto y/o giro"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["De poder", "De habilidad"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 3,
        "nombre": "Examen 3\u00b0 GUP - Cintur\u00f3n Azul punta roja",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Yul-Gok", "Joong-Gun"],
            "Sambo Matsokgi": ["Sambo Matsokgi"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["De brazos", "De piernas"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto y/o giro"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["De poder", "De habilidad"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 2,
        "nombre": "Examen 2\u00b0 GUP - Cintur\u00f3n Rojo",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Joong-Gun", "Toi-Gye"],
            "Sambo Matsokgi": ["Sambo Matsokgi"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["De brazos", "De piernas"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto y/o giro"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Sin armas", "Con armas"],
            "Rotura": ["De poder", "De habilidad"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
    {
        "numeracion": 1,
        "nombre": "Examen 1\u00b0 GUP - Cintur\u00f3n Rojo punta negra",
        "secciones": {
            "Ejercicios fundamentales": ["Ejercicios fundamentales"],
            "Tul": ["Toi-Gye", "Hwa-Rang"],
            "Sambo Matsokgi": ["1 sentido", "2 sentidos"],
            "Ibo Matsokgi": ["Ibo Matsokgi"],
            "Ilbo Matsokgi": ["De brazos", "De piernas"],
            "T\u00e9cnicas de patadas": ["Sin salto", "Con salto y/o giro"],
            "Jayu Matsokgi": ["Jayu Matsokgi"],
            "Hosin Sool": ["Hosin Sool"],
            "Rotura": ["De poder", "De habilidad"],
            "Teor\u00eda": ["Teor\u00eda"],
            "Actitud": ["Actitud"],
        },
    },
]


def cargar_templates_examenes_color(apps, schema_editor):
    Cinturon = apps.get_model("alumnos", "Cinturon")
    ExamenTemplate = apps.get_model("alumnos", "ExamenTemplate")
    ExamenTemplateSeccion = apps.get_model("alumnos", "ExamenTemplateSeccion")
    ExamenTemplateItem = apps.get_model("alumnos", "ExamenTemplateItem")

    for template_data in TEMPLATES_GUP:
        numeracion = template_data["numeracion"]
        try:
            cinturon = Cinturon.objects.get(tipo_rango="GUP", numeracion=numeracion)
        except Cinturon.DoesNotExist as exc:
            raise ValueError(f"Falta el cinturon GUP {numeracion}.") from exc

        template, _ = ExamenTemplate.objects.update_or_create(
            cinturon=cinturon,
            nombre=template_data["nombre"],
            version=1,
            defaults={
                "descripcion": DESCRIPCION_TEMPLATE,
                "nota_minima_aprobacion": None,
                "activo": True,
            },
        )

        for seccion_orden, seccion_nombre in enumerate(SECCIONES_ORDEN, start=1):
            items = template_data["secciones"].get(seccion_nombre, [])
            if not items:
                continue
            seccion, _ = ExamenTemplateSeccion.objects.update_or_create(
                examen_template=template,
                nombre=seccion_nombre,
                defaults={
                    "descripcion": None,
                    "orden": seccion_orden,
                    "obligatorio": True,
                    "activo": True,
                },
            )

            for item_orden, item_nombre in enumerate(items, start=1):
                ExamenTemplateItem.objects.update_or_create(
                    seccion=seccion,
                    nombre=item_nombre,
                    defaults={
                        "descripcion": None,
                        "tipo_evaluacion": "CONCEPTO",
                        "orden": item_orden,
                        "puntaje_maximo": None,
                        "ponderacion": 1,
                        "obligatorio": True,
                        "activo": True,
                    },
                )


def no_borrar_templates(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("alumnos", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(cargar_templates_examenes_color, no_borrar_templates),
    ]
