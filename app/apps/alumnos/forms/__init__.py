from .alumno_forms import AlumnoForm
from .base import TailwindModelForm
from .credencial_forms import BloquearAccesoMobileAlumnoForm, GenerarCredencialesAlumnoForm, ResetearPasswordAlumnoForm
from .examen_forms import CrearExamenForm
from .examen_template_forms import ExamenTemplateForm, ExamenTemplateItemForm, ExamenTemplateSeccionForm

__all__ = ["AlumnoForm", "TailwindModelForm", "BloquearAccesoMobileAlumnoForm",
           "GenerarCredencialesAlumnoForm", "ResetearPasswordAlumnoForm", "CrearExamenForm",
           "ExamenTemplateForm", "ExamenTemplateItemForm", "ExamenTemplateSeccionForm"]
