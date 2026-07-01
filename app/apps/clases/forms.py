from django import forms

from apps.alumnos.models import AlumnoEscuela
from apps.escuelas.models import Escuela, EscuelaDocente

from .models import AsistenciaClase, Clase, ClaseHorario, ClaseSesion


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


class ClaseForm(TailwindModelForm):
    class Meta:
        model = Clase
        fields = [
            "escuela",
            "nombre",
            "descripcion",
            "docente_responsable",
            "cupo_maximo",
            "activo",
        ]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, escuela=None, permitir_escuela=False, **kwargs):
        super().__init__(*args, **kwargs)
        if permitir_escuela:
            self.fields["escuela"].queryset = Escuela.objects.filter(activo=True)
            self.fields["escuela"].required = True
        else:
            self.fields.pop("escuela")

        escuela_seleccionada = escuela
        if permitir_escuela and not escuela_seleccionada and self.is_bound:
            escuela_id = self.data.get(self.add_prefix("escuela"))
            escuela_seleccionada = Escuela.objects.filter(pk=escuela_id, activo=True).first()

        queryset = EscuelaDocente.objects.select_related("docente__usuario", "escuela").filter(
            activo=True,
            docente__activo=True,
            escuela__activo=True,
        )
        if escuela_seleccionada:
            queryset = queryset.filter(escuela=escuela_seleccionada)
        self.fields["docente_responsable"].queryset = queryset
        self.fields["docente_responsable"].required = False

    def clean(self):
        cleaned_data = super().clean()
        escuela = cleaned_data.get("escuela") or getattr(self.instance, "escuela", None)
        docente_responsable = cleaned_data.get("docente_responsable")
        if (
            escuela
            and docente_responsable
            and docente_responsable.escuela_id != escuela.id
        ):
            self.add_error(
                "docente_responsable",
                "El docente responsable debe pertenecer a la escuela seleccionada.",
            )
        return cleaned_data


class ClaseHorarioForm(TailwindModelForm):
    class Meta:
        model = ClaseHorario
        fields = ["dia_semana", "hora_inicio", "hora_fin", "fecha_desde", "fecha_hasta", "activo"]
        widgets = {
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}),
            "fecha_desde": forms.DateInput(attrs={"type": "date"}),
            "fecha_hasta": forms.DateInput(attrs={"type": "date"}),
        }


class ClaseAlumnoForm(forms.Form):
    alumno_escuela = forms.ModelChoiceField(queryset=AlumnoEscuela.objects.none())
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, alumnos_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["alumno_escuela"].queryset = alumnos_queryset or AlumnoEscuela.objects.none()
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", INPUT_CLASS)


class ClaseExtraForm(TailwindModelForm):
    class Meta:
        model = ClaseSesion
        fields = ["fecha", "hora_inicio", "hora_fin", "docente_a_cargo", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time"}),
            "hora_fin": forms.TimeInput(attrs={"type": "time"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, escuela=None, **kwargs):
        super().__init__(*args, **kwargs)
        docentes = EscuelaDocente.objects.select_related("docente__usuario").filter(
            activo=True,
            docente__activo=True,
            escuela__activo=True,
        )
        if escuela:
            docentes = docentes.filter(escuela=escuela)
        self.fields["docente_a_cargo"].queryset = docentes
        self.fields["docente_a_cargo"].required = False


class CancelarSesionForm(forms.Form):
    motivo = forms.CharField(widget=forms.Textarea(attrs={"rows": 3, "class": INPUT_CLASS}))


class AsistenciaLineaForm(forms.Form):
    estado = forms.ChoiceField(choices=AsistenciaClase.Estado.choices)
    observaciones = forms.CharField(required=False)
