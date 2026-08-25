from apps.usuarios.models import Docente
from ..models import EscuelaDocente

def docentes_para_listado():
    return Docente.objects.select_related("usuario").prefetch_related("escuelas__escuela")

def relaciones_con_detalle():
    return EscuelaDocente.objects.select_related("docente", "escuela")
