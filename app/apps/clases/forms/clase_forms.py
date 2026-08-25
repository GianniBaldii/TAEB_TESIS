from django import forms
from apps.escuelas.models import Escuela, EscuelaDocente
from ..models import Clase, ClaseSesion
from .base import TailwindModelForm
class ClaseForm(TailwindModelForm):
    class Meta:
        model = Clase
        fields = ["escuela", "nombre", "descripcion", "docente_responsable", "cupo_maximo", "activo"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3})}
    def __init__(self, *args, escuela=None, permitir_escuela=False, **kwargs):
        super().__init__(*args, **kwargs)
        if permitir_escuela:
            self.fields["escuela"].queryset = Escuela.objects.filter(activo=True)
            self.fields["escuela"].required = True
        else: self.fields.pop("escuela")
        escuela_obj = escuela
        if permitir_escuela and not escuela_obj and self.is_bound:
            escuela_obj = Escuela.objects.filter(pk=self.data.get(self.add_prefix("escuela")), activo=True).first()
        docentes = EscuelaDocente.objects.select_related("docente__usuario", "escuela").filter(activo=True, docente__activo=True, escuela__activo=True)
        if escuela_obj: docentes = docentes.filter(escuela=escuela_obj)
        self.fields["docente_responsable"].queryset = docentes
        self.fields["docente_responsable"].required = False
    def clean(self):
        data = super().clean()
        escuela = data.get("escuela") or getattr(self.instance, "escuela", None)
        docente = data.get("docente_responsable")
        if escuela and docente and docente.escuela_id != escuela.id:
            self.add_error("docente_responsable", "El docente responsable debe pertenecer a la escuela seleccionada.")
        return data
class ClaseExtraForm(TailwindModelForm):
    class Meta:
        model = ClaseSesion
        fields = ["fecha", "hora_inicio", "hora_fin", "docente_a_cargo", "observaciones"]
        widgets = {"fecha": forms.DateInput(attrs={"type": "date"}), "hora_inicio": forms.TimeInput(attrs={"type": "time"}), "hora_fin": forms.TimeInput(attrs={"type": "time"}), "observaciones": forms.Textarea(attrs={"rows": 3})}
    def __init__(self, *args, escuela=None, **kwargs):
        super().__init__(*args, **kwargs)
        docentes = EscuelaDocente.objects.select_related("docente__usuario").filter(activo=True, docente__activo=True, escuela__activo=True)
        if escuela: docentes = docentes.filter(escuela=escuela)
        self.fields["docente_a_cargo"].queryset = docentes
        self.fields["docente_a_cargo"].required = False
