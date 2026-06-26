from datetime import date
from statistics import median

from django.utils import timezone

from apps.alumnos.constants.progreso_taekwondo import (
    DIAS_MES_REFERENCIA,
    DIAS_RECIEN_PROMOVIDO,
    ESTADOS_HABILITACION,
    GLOSARIO_TIEMPOS_ORIENTATIVOS,
    TIEMPOS_ORIENTATIVOS_POR_CINTURON,
    UMBRAL_PROXIMO_A_HABILITARSE,
    UMBRAL_TIEMPO_EXCEDIDO,
    EstadoHabilitacion,
)
from apps.alumnos.models import Examen

from . import alumno_service


def _hoy():
    return timezone.localdate()


def _dias_a_meses(dias):
    if dias is None:
        return None
    return round(dias / DIAS_MES_REFERENCIA, 1)


def _formatear_duracion(dias):
    if dias is None:
        return "-"
    if dias == 0:
        return "Hoy"
    if dias < 30:
        return f"{dias} días"
    meses = _dias_a_meses(dias)
    if meses < 12:
        if float(meses).is_integer():
            meses = int(meses)
        return f"{meses} meses"
    anios = round(meses / 12, 1)
    if float(anios).is_integer():
        anios = int(anios)
    return f"{anios} años"


def _grado_cinturon(cinturon):
    if not cinturon:
        return "-"
    if cinturon.tipo_rango == "DAN":
        return f"{cinturon.numeracion}° dan"
    return f"{cinturon.numeracion}° gup"


def obtener_tiempo_orientativo_para_siguiente_examen(cinturon_actual):
    if not cinturon_actual:
        return None
    return TIEMPOS_ORIENTATIVOS_POR_CINTURON.get(
        (cinturon_actual.tipo_rango, cinturon_actual.numeracion)
    )


def obtener_ultimo_hito_historial(alumno):
    return (
        alumno.historial_cinturones.select_related("cinturon", "examen")
        .order_by("-fecha_obtencion", "-cinturon__orden", "-fecha_creacion")
        .first()
    )


def obtener_fecha_ultimo_cinturon(alumno):
    ultimo_hito = obtener_ultimo_hito_historial(alumno)
    if ultimo_hito:
        return ultimo_hito.fecha_obtencion
    return alumno.fecha_inicio_taekwondo


def obtener_dias_desde_ultimo_cinturon(alumno, fecha_referencia=None):
    fecha_ultimo_cinturon = obtener_fecha_ultimo_cinturon(alumno)
    if not fecha_ultimo_cinturon:
        return None
    fecha_referencia = fecha_referencia or _hoy()
    return max((fecha_referencia - fecha_ultimo_cinturon).days, 0)


def obtener_meses_desde_ultimo_cinturon(alumno, fecha_referencia=None):
    return _dias_a_meses(
        obtener_dias_desde_ultimo_cinturon(alumno, fecha_referencia=fecha_referencia)
    )


def obtener_proximo_cinturon(alumno):
    return alumno_service.obtener_siguiente_cinturon(alumno.cinturon_actual)


def _estado_base(codigo):
    datos = ESTADOS_HABILITACION[codigo]
    return {
        "codigo": codigo,
        "label": datos["label"],
        "color": datos["color"],
        "classes": datos["classes"],
        "badge_classes": datos["badge_classes"],
    }


def obtener_estado_habilitacion_rendir(alumno, fecha_referencia=None):
    if not alumno.cinturon_actual:
        estado = _estado_base(EstadoHabilitacion.SIN_DATOS)
        estado["mensaje"] = "El alumno todavía no tiene un cinturón actual registrado."
        estado["porcentaje"] = 0
        return estado

    proximo_cinturon = obtener_proximo_cinturon(alumno)
    if not proximo_cinturon:
        estado = _estado_base(EstadoHabilitacion.SIN_PROXIMO_CINTURON)
        estado["mensaje"] = "No hay un próximo cinturón activo configurado para este alumno."
        estado["porcentaje"] = 100
        return estado

    tiempo_orientativo = obtener_tiempo_orientativo_para_siguiente_examen(
        alumno.cinturon_actual
    )
    dias_transcurridos = obtener_dias_desde_ultimo_cinturon(
        alumno, fecha_referencia=fecha_referencia
    )
    if not tiempo_orientativo or dias_transcurridos is None:
        estado = _estado_base(EstadoHabilitacion.SIN_DATOS)
        estado["mensaje"] = (
            "No hay una fecha confiable de inicio o última promoción para calcular "
            "la habilitación orientativa."
        )
        estado["porcentaje"] = 0
        return estado

    dias_minimos = tiempo_orientativo.dias_minimos
    porcentaje = min(round((dias_transcurridos / dias_minimos) * 100), 999)

    if dias_transcurridos < DIAS_RECIEN_PROMOVIDO:
        codigo = EstadoHabilitacion.RECIEN_PROMOVIDO
        mensaje = (
            "El alumno fue promovido recientemente. Este indicador es solo una "
            "referencia temporal para acompañar la planificación."
        )
    elif tiempo_orientativo.dias_maximos and dias_transcurridos > tiempo_orientativo.dias_maximos:
        codigo = EstadoHabilitacion.TIEMPO_EXCEDIDO
        mensaje = (
            "El alumno ya superó la ventana orientativa máxima para este cinturón. "
            "Puede ser un buen momento para revisar su proceso con criterio docente."
        )
    elif dias_transcurridos < dias_minimos * UMBRAL_PROXIMO_A_HABILITARSE:
        codigo = EstadoHabilitacion.AUN_NO_HABILITADO
        mensaje = (
            "Todavía no alcanzó el tiempo orientativo mínimo para el próximo examen."
        )
    elif dias_transcurridos < dias_minimos:
        codigo = EstadoHabilitacion.PROXIMO_A_HABILITARSE
        mensaje = (
            "El alumno se está acercando a la ventana orientativa para rendir."
        )
    elif tiempo_orientativo.dias_maximos and dias_transcurridos <= tiempo_orientativo.dias_maximos:
        codigo = EstadoHabilitacion.HABILITADO_ORIENTATIVAMENTE
        mensaje = (
            "El alumno se encuentra dentro de la ventana orientativa para rendir "
            "el próximo examen."
        )
    elif dias_transcurridos <= dias_minimos * UMBRAL_TIEMPO_EXCEDIDO:
        codigo = EstadoHabilitacion.HABILITADO_ORIENTATIVAMENTE
        mensaje = (
            "El alumno ya alcanzó el tiempo orientativo para rendir el próximo examen."
        )
    else:
        codigo = EstadoHabilitacion.TIEMPO_EXCEDIDO
        mensaje = (
            "El alumno superó ampliamente el tiempo orientativo de preparación."
        )

    estado = _estado_base(codigo)
    estado["mensaje"] = mensaje
    estado["porcentaje"] = porcentaje
    return estado


def obtener_intervalos_historicos_entre_promociones(alumno):
    historial = list(
        alumno.historial_cinturones.select_related("cinturon")
        .order_by("fecha_obtencion", "cinturon__orden")
    )
    intervalos = []
    anterior = None
    for hito in historial:
        if anterior:
            dias = max((hito.fecha_obtencion - anterior.fecha_obtencion).days, 0)
            intervalos.append(
                {
                    "desde": anterior,
                    "hasta": hito,
                    "dias": dias,
                    "meses": _dias_a_meses(dias),
                    "texto": _formatear_duracion(dias),
                }
            )
        anterior = hito
    return intervalos


def obtener_promedio_historico_promociones(alumno):
    intervalos = obtener_intervalos_historicos_entre_promociones(alumno)
    if not intervalos:
        return None
    return round(sum(intervalo["dias"] for intervalo in intervalos) / len(intervalos))


def obtener_mediana_historica_promociones(alumno):
    intervalos = obtener_intervalos_historicos_entre_promociones(alumno)
    if not intervalos:
        return None
    return round(median(intervalo["dias"] for intervalo in intervalos))


def _comparacion_historica(dias_actuales, promedio_dias):
    if dias_actuales is None or promedio_dias is None:
        return "No hay datos históricos suficientes para comparar su trayectoria."
    if dias_actuales > promedio_dias * 1.2:
        return "El alumno ya superó el tiempo promedio que suele tardar entre promociones."
    if dias_actuales < promedio_dias * 0.8:
        return "Todavía se encuentra dentro de un tiempo menor a su promedio histórico."
    return "Actualmente el alumno lleva un ritmo similar a su historial."


def _ultimo_examen(alumno):
    return alumno.examenes.select_related("cinturon_destino").order_by(
        "-fecha_examen", "-fecha_creacion"
    ).first()


def construir_timeline_historial(alumno):
    historial = list(
        alumno.historial_cinturones.select_related("cinturon", "examen")
        .order_by("fecha_obtencion", "cinturon__orden")
    )
    if not historial:
        return []

    fecha_inicio = alumno.fecha_inicio_taekwondo or historial[0].fecha_obtencion
    timeline = []
    anterior = None
    for indice, hito in enumerate(historial):
        dias_desde_anterior = (
            None
            if anterior is None
            else max((hito.fecha_obtencion - anterior.fecha_obtencion).days, 0)
        )
        dias_acumulados = max((hito.fecha_obtencion - fecha_inicio).days, 0)
        timeline.append(
            {
                "hito": hito,
                "cinturon": hito.cinturon,
                "grado": _grado_cinturon(hito.cinturon),
                "fecha": hito.fecha_obtencion,
                "examen": hito.examen,
                "observaciones": hito.observaciones,
                "es_primero": indice == 0,
                "tiempo_desde_anterior_dias": dias_desde_anterior,
                "tiempo_desde_anterior": (
                    "Primera promoción registrada"
                    if anterior is None
                    else f"{_formatear_duracion(dias_desde_anterior)} desde el cinturón anterior"
                ),
                "tiempo_acumulado_dias": dias_acumulados,
                "tiempo_acumulado": f"Acumulado desde el inicio: {_formatear_duracion(dias_acumulados)}",
            }
        )
        anterior = hito
    return timeline


def _resumen_historial(alumno, timeline):
    ultimo = timeline[-1] if timeline else None
    fecha_inicio = alumno.fecha_inicio_taekwondo or (timeline[0]["fecha"] if timeline else None)
    fecha_ultimo = ultimo["fecha"] if ultimo else None
    tiempo_total_dias = (
        max((fecha_ultimo - fecha_inicio).days, 0)
        if fecha_inicio and fecha_ultimo
        else None
    )
    return {
        "cinturon_actual": alumno.cinturon_actual,
        "promociones_obtenidas": len(timeline),
        "fecha_ultimo_cinturon": fecha_ultimo,
        "tiempo_total_dias": tiempo_total_dias,
        "tiempo_total": _formatear_duracion(tiempo_total_dias),
    }


def _glosario_con_cinturones_reales():
    return GLOSARIO_TIEMPOS_ORIENTATIVOS


def obtener_analisis_trayectoria(alumno, fecha_referencia: date | None = None):
    fecha_referencia = fecha_referencia or _hoy()
    timeline = construir_timeline_historial(alumno)
    resumen_examenes = alumno_service.obtener_resumen_examenes(alumno)
    dias_desde_ultimo = obtener_dias_desde_ultimo_cinturon(
        alumno, fecha_referencia=fecha_referencia
    )
    tiempo_orientativo = obtener_tiempo_orientativo_para_siguiente_examen(
        alumno.cinturon_actual
    )
    promedio_historico = obtener_promedio_historico_promociones(alumno)
    mediana_historica = obtener_mediana_historica_promociones(alumno)
    estado = obtener_estado_habilitacion_rendir(alumno, fecha_referencia=fecha_referencia)
    ultimo_examen = _ultimo_examen(alumno)
    proximo_cinturon = obtener_proximo_cinturon(alumno)

    return {
        "cinturon_actual": alumno.cinturon_actual,
        "proximo_cinturon": proximo_cinturon,
        "fecha_ultimo_cinturon": obtener_fecha_ultimo_cinturon(alumno),
        "dias_desde_ultimo_cinturon": dias_desde_ultimo,
        "meses_desde_ultimo_cinturon": _dias_a_meses(dias_desde_ultimo),
        "tiempo_desde_ultimo_cinturon": _formatear_duracion(dias_desde_ultimo),
        "tiempo_orientativo": tiempo_orientativo,
        "tiempo_orientativo_meses": tiempo_orientativo.meses_minimos if tiempo_orientativo else None,
        "tiempo_orientativo_label": tiempo_orientativo.descripcion if tiempo_orientativo else "-",
        "estado_habilitacion": estado,
        "porcentaje_progreso": min(estado.get("porcentaje", 0), 100),
        "promociones_obtenidas": len(timeline),
        "cantidad_examenes": sum(resumen_examenes.values()),
        "cantidad_aprobados": resumen_examenes.get("aprobados", 0),
        "cantidad_desaprobados": resumen_examenes.get("desaprobados", 0),
        "cantidad_pendientes": resumen_examenes.get("pendientes", 0),
        "ultimo_examen": ultimo_examen,
        "promedio_historico_dias": promedio_historico,
        "promedio_historico": _formatear_duracion(promedio_historico),
        "mediana_historica_dias": mediana_historica,
        "mediana_historica": _formatear_duracion(mediana_historica),
        "comparacion_historica": _comparacion_historica(
            dias_desde_ultimo, promedio_historico
        ),
        "timeline_historial": timeline,
        "resumen_historial": _resumen_historial(alumno, timeline),
        "glosario_tiempos": _glosario_con_cinturones_reales(),
        "referencia_texto": (
            "Referencia orientativa. Los tiempos reales pueden variar según asistencia, "
            "criterio del instructor, edad, rendimiento y reglamento de cada escuela."
        ),
        "estados_finales_examen": [
            Examen.Estado.APROBADO,
            Examen.Estado.DESAPROBADO,
            Examen.Estado.AUSENTE,
            Examen.Estado.ANULADO,
        ],
    }
