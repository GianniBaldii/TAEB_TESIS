from apps.escuelas.services.acceso_escuela_service import obtener_escuela_activa_usuario

from ..models import Alumno, AlumnoEscuela, Examen


def alumno_queryset():
    return Alumno.objects.select_related("cinturon_actual")


def inscripciones_visibles_para_usuario(usuario, *, incluir_inactivas=False):
    inscripciones = AlumnoEscuela.objects.select_related(
        "alumno", "alumno__cinturon_actual", "escuela"
    )
    if not usuario.is_superuser:
        inscripciones = inscripciones.filter(
            escuela=obtener_escuela_activa_usuario(usuario)
        )
    if not incluir_inactivas:
        inscripciones = inscripciones.filter(activo=True)
    return inscripciones


def examenes_del_alumno(alumno):
    return Examen.objects.filter(alumno=alumno).select_related(
        "alumno", "examen_template", "cinturon_origen", "cinturon_destino"
    )
