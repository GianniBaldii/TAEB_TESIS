from django.db import transaction
from django.db.models import Count, Q

from apps.alumnos.models import Alumno, AlumnoCinturonHistorial, Cinturon, Examen


ALUMNO_CAMPOS_EDITABLES = {
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
}


def _normalizar_data(data):
    return {campo: valor for campo, valor in data.items() if campo in ALUMNO_CAMPOS_EDITABLES}


def obtener_cinturon_inicial():
    """Obtiene el cinturón activo de menor orden (normalmente, blanco)."""
    return Cinturon.objects.filter(activo=True).order_by("orden").first()


def crear_alumno(data):
    datos = _normalizar_data(data)
    if not datos.get("cinturon_actual"):
        cinturon_inicial = obtener_cinturon_inicial()
        if not cinturon_inicial:
            raise ValueError("No existe un cinturón activo para asignar al alumno.")
        datos["cinturon_actual"] = cinturon_inicial
    return Alumno.objects.create(**datos)


def actualizar_alumno(alumno, data):
    for campo, valor in _normalizar_data(data).items():
        setattr(alumno, campo, valor)
    alumno.save(update_fields=[*list(_normalizar_data(data).keys()), "fecha_modificacion"])
    return alumno


def dar_baja_alumno(alumno):
    alumno.activo = False
    alumno.save(update_fields=["activo", "fecha_modificacion"])
    return alumno


def reactivar_alumno(alumno):
    alumno.activo = True
    alumno.save(update_fields=["activo", "fecha_modificacion"])
    return alumno


def obtener_siguiente_cinturon(cinturon_actual):
    cinturones = Cinturon.objects.filter(activo=True)
    if cinturon_actual:
        return cinturones.filter(orden__gt=cinturon_actual.orden).order_by("orden").first()
    return cinturones.order_by("orden").first()


def obtener_cinturon_anterior(cinturon):
    """Devuelve el cinturón activo inmediatamente anterior en la graduación."""
    if not cinturon:
        return None
    return (
        Cinturon.objects.filter(activo=True, orden__lt=cinturon.orden)
        .order_by("-orden")
        .first()
    )


def obtener_ultimo_examen(alumno):
    return alumno.examenes.select_related("cinturon_destino").order_by(
        "-fecha_examen", "-fecha_creacion"
    ).first()


def obtener_resumen_examenes(alumno):
    conteos = alumno.examenes.aggregate(
        aprobados=Count("id", filter=Q(estado=Examen.Estado.APROBADO)),
        desaprobados=Count("id", filter=Q(estado=Examen.Estado.DESAPROBADO)),
        pendientes=Count("id", filter=Q(estado=Examen.Estado.PENDIENTE)),
        anulados=Count("id", filter=Q(estado=Examen.Estado.ANULADO)),
        ausentes=Count("id", filter=Q(estado=Examen.Estado.AUSENTE)),
    )
    return {clave: valor or 0 for clave, valor in conteos.items()}


def obtener_progreso_alumno(alumno):
    return {
        "cinturon_actual": alumno.cinturon_actual,
        "proximo_cinturon": obtener_siguiente_cinturon(alumno.cinturon_actual),
        "ultimo_examen": obtener_ultimo_examen(alumno),
        "resumen_examenes": obtener_resumen_examenes(alumno),
    }


@transaction.atomic
def registrar_cambio_cinturon_por_examen(examen):
    alumno = examen.alumno
    debe_actualizar_cinturon = (
        not alumno.cinturon_actual
        or examen.cinturon_destino.orden > alumno.cinturon_actual.orden
        or not examen.es_historico
    )
    if debe_actualizar_cinturon:
        alumno.cinturon_actual = examen.cinturon_destino
        alumno.save(update_fields=["cinturon_actual", "fecha_modificacion"])
    historial, _ = AlumnoCinturonHistorial.objects.get_or_create(
        alumno=alumno,
        cinturon=examen.cinturon_destino,
        defaults={
            "examen": examen,
            "fecha_obtencion": examen.fecha_examen,
            "observaciones": examen.observaciones,
        },
    )
    return historial
