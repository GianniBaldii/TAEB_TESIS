from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.alumnos.models import AlumnoEscuela

from ..models import ClaseAlumno
from .excepciones import ClasesError


def _validar_alumno_para_clase(clase, alumno_escuela):
    if not clase.activo:
        raise ClasesError("No se pueden inscribir alumnos a una clase inactiva.")
    if clase.escuela_id != alumno_escuela.escuela_id:
        raise ClasesError("El alumno debe pertenecer a la misma escuela de la clase.")
    if not alumno_escuela.activo:
        raise ClasesError("El alumno no tiene una inscripcion activa en la escuela.")
    if hasattr(alumno_escuela, "alumno") and not alumno_escuela.alumno.activo:
        raise ClasesError("El alumno se encuentra inactivo.")


@transaction.atomic
def inscribir_alumno_en_clase(clase, alumno_escuela, observaciones=None):
    _validar_alumno_para_clase(clase, alumno_escuela)
    inscripcion, creada = ClaseAlumno.objects.get_or_create(
        clase=clase,
        alumno_escuela=alumno_escuela,
        defaults={"activo": True, "observaciones": observaciones},
    )
    if creada:
        return inscripcion
    if inscripcion.activo:
        raise ClasesError("El alumno ya esta inscripto en esta clase.")
    return reactivar_alumno_en_clase(inscripcion, observaciones=observaciones)


def dar_baja_alumno_de_clase(clase_alumno):
    clase_alumno.activo = False
    clase_alumno.fecha_baja = timezone.localdate()
    clase_alumno.save(update_fields=["activo", "fecha_baja", "fecha_modificacion"])
    return clase_alumno


def reactivar_alumno_en_clase(clase_alumno, observaciones=None):
    _validar_alumno_para_clase(clase_alumno.clase, clase_alumno.alumno_escuela)
    clase_alumno.activo = True
    clase_alumno.fecha_baja = None
    if observaciones is not None:
        clase_alumno.observaciones = observaciones
    clase_alumno.save(
        update_fields=["activo", "fecha_baja", "observaciones", "fecha_modificacion"]
    )
    return clase_alumno


def obtener_alumnos_disponibles_para_clase(clase, termino_busqueda=None):
    alumnos = AlumnoEscuela.objects.select_related("alumno", "alumno__cinturon_actual").filter(
        escuela=clase.escuela,
        activo=True,
        alumno__activo=True,
    )
    activos_en_clase = ClaseAlumno.objects.filter(clase=clase, activo=True).values(
        "alumno_escuela_id"
    )
    alumnos = alumnos.exclude(pk__in=activos_en_clase)
    if termino_busqueda:
        alumnos = alumnos.filter(
            Q(alumno__nombre__icontains=termino_busqueda)
            | Q(alumno__apellido__icontains=termino_busqueda)
            | Q(alumno__dni__icontains=termino_busqueda)
        )
    return alumnos


def obtener_alumnos_activos_de_clase(clase, fecha_referencia=None):
    alumnos = ClaseAlumno.objects.select_related(
        "alumno_escuela",
        "alumno_escuela__alumno",
        "alumno_escuela__alumno__cinturon_actual",
    ).filter(clase=clase)
    if fecha_referencia:
        alumnos = alumnos.filter(fecha_alta__lte=fecha_referencia).filter(
            Q(activo=True) | Q(fecha_baja__isnull=True) | Q(fecha_baja__gte=fecha_referencia)
        )
    else:
        alumnos = alumnos.filter(activo=True)
    return alumnos

