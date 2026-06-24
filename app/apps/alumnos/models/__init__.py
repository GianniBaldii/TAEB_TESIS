from .alumno import Alumno
from .alumno_escuela import AlumnoEscuela
from .cinturon import Cinturon
from .examen import Examen, ExamenDetalle
from .examen_template import ExamenTemplate, ExamenTemplateItem, ExamenTemplateSeccion
from .historial import AlumnoCinturonHistorial

__all__ = [
    "Alumno",
    "AlumnoEscuela",
    "AlumnoCinturonHistorial",
    "Cinturon",
    "Examen",
    "ExamenDetalle",
    "ExamenTemplate",
    "ExamenTemplateItem",
    "ExamenTemplateSeccion",
]
