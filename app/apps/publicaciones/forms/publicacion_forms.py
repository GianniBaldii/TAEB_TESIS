from django import forms

from apps.escuelas.models import Escuela

from ..models import Publicacion


INPUT_CLASS = (
    "block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
    "text-slate-900 shadow-sm outline-none transition focus:border-blue-500 "
    "focus:ring-2 focus:ring-blue-500/20"
)


class PublicacionForm(forms.ModelForm):
    fecha_hora_inicio = forms.SplitDateTimeField(
        label="Inicio",
        required=False,
        widget=forms.SplitDateTimeWidget(
            date_format="%Y-%m-%d",
            time_format="%H:%M",
            date_attrs={"type": "date", "class": INPUT_CLASS},
            time_attrs={"type": "time", "class": INPUT_CLASS},
        ),
    )
    fecha_hora_fin = forms.SplitDateTimeField(
        label="Finalización",
        required=False,
        widget=forms.SplitDateTimeWidget(
            date_format="%Y-%m-%d",
            time_format="%H:%M",
            date_attrs={"type": "date", "class": INPUT_CLASS},
            time_attrs={"type": "time", "class": INPUT_CLASS},
        ),
    )

    class Meta:
        model = Publicacion
        fields = [
            "escuela",
            "titulo",
            "descripcion",
            "tipo_publicacion",
            "tematica",
            "fecha_hora_inicio",
            "fecha_hora_fin",
            "ubicacion",
            "cupo_maximo",
        ]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, permitir_escuela=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cupo_maximo"].label = (
        "Cupo máximo de participantes (opcional)"
        )
        if permitir_escuela:
            self.fields["escuela"].queryset = Escuela.objects.filter(activo=True)
        else:
            self.fields.pop("escuela")
        for nombre, field in self.fields.items():
            if nombre not in {"fecha_hora_inicio", "fecha_hora_fin"}:
                field.widget.attrs.setdefault("class", INPUT_CLASS)

    def clean(self):
        data = super().clean()
        tipo = data.get("tipo_publicacion")
        inicio = data.get("fecha_hora_inicio")
        fin = data.get("fecha_hora_fin")
        ubicacion = data.get("ubicacion")
        cupo = data.get("cupo_maximo")
        if tipo == Publicacion.Tipo.EVENTO and not inicio:
            self.add_error("fecha_hora_inicio", "La fecha y hora de inicio son obligatorias para un evento.")
        if fin and not inicio:
            self.add_error("fecha_hora_fin", "Para indicar una finalización primero debe indicar el inicio.")
        elif inicio and fin and fin <= inicio:
            self.add_error("fecha_hora_fin", "La finalización debe ser posterior al inicio.")
        if tipo == Publicacion.Tipo.ANUNCIO:
            if ubicacion:
                self.add_error("ubicacion", "La ubicación solo corresponde a publicaciones de tipo evento.")
            if cupo is not None:
                self.add_error("cupo_maximo", "El cupo máximo solo corresponde a publicaciones de tipo evento.")
        return data
