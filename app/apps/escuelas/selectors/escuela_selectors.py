from ..models import Escuela

def escuelas_para_listado():
    return Escuela.objects.all()
