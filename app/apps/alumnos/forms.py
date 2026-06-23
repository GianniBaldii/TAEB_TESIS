from django import forms

from .models import (
    Alumno,
    Cinturon,
    ExamenTemplate,
    ExamenTemplateItem,
    ExamenTemplateSeccion,
)


INPUT_CLASS = (
    "block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
    "text-slate-900 shadow-sm outline-none transition focus:border-blue-500 "
    "focus:ring-2 focus:ring-blue-500/20"
)
CHECK_CLASS = "h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"


class TailwindModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", CHECK_CLASS)
            else:
                field.widget.attrs.setdefault("class", INPUT_CLASS)


class AlumnoForm(TailwindModelForm):
    class Meta:
        model = Alumno
        fields = [
            "nombre",
            "apellido",
            "dni",
            "fecha_nacimiento",
            "fecha_inicio_taekwondo",
            "email",
            "telefono",
            "direccion",
            "peso_aproximado",
            "altura_aproximada",
            "cinturon_actual",
            "activo",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "fecha_inicio_taekwondo": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_inicio_taekwondo"].label = "Fecha de inicio en Taekwondo"
        self.fields["cinturon_actual"].help_text = (
            "Déjelo vacío para asignar automáticamente el cinturón inicial. "
            "Seleccione otro solo si viene de otra escuela."
        )


class ExamenTemplateForm(TailwindModelForm):
    class Meta:
        model = ExamenTemplate
        fields = [
            "cinturon",
            "nombre",
            "descripcion",
            "nota_minima_aprobacion",
            "vigente_desde",
            "vigente_hasta",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "vigente_desde": forms.DateInput(attrs={"type": "date"}),
            "vigente_hasta": forms.DateInput(attrs={"type": "date"}),
        }


class ExamenTemplateSeccionForm(TailwindModelForm):
    class Meta:
        model = ExamenTemplateSeccion
        fields = ["nombre", "descripcion", "orden", "obligatorio", "activo"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}


class ExamenTemplateItemForm(TailwindModelForm):
    class Meta:
        model = ExamenTemplateItem
        fields = [
            "nombre",
            "descripcion",
            "tipo_evaluacion",
            "orden",
            "puntaje_maximo",
            "ponderacion",
            "obligatorio",
            "activo",
        ]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}


class CrearExamenForm(forms.Form):
    fecha_examen = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    lugar = forms.CharField(max_length=150, required=False)
    es_historico = forms.BooleanField(
        required=False,
        label="Carga historica",
        help_text=(
            "Usar para examenes ya rendidos antes de cargar el alumno en TAEB."
        ),
    )
    cinturon_destino = forms.ModelChoiceField(
        queryset=Cinturon.objects.filter(activo=True),
        required=False,
        label="Cinturon destino",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)
        self.fields["es_historico"].widget.attrs["x-model"] = "historico"

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("es_historico") and not cleaned_data.get("cinturon_destino"):
            self.add_error(
                "cinturon_destino",
                "Seleccione el cinturón destino para el examen histórico.",
            )
        return cleaned_data
