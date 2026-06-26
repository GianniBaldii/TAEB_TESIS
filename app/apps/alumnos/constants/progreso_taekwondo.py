"""Referencias orientativas para analizar la trayectoria taekwondista.

Estos valores no son reglas duras de negocio. Sirven para mostrar indicadores
visuales y ayudar al docente a interpretar el progreso del alumno.
"""

from dataclasses import dataclass


DIAS_MES_REFERENCIA = 30.44
DIAS_RECIEN_PROMOVIDO = 30
UMBRAL_PROXIMO_A_HABILITARSE = 0.8
UMBRAL_TIEMPO_EXCEDIDO = 1.5


class EstadoHabilitacion:
    SIN_DATOS = "SIN_DATOS"
    SIN_PROXIMO_CINTURON = "SIN_PROXIMO_CINTURON"
    RECIEN_PROMOVIDO = "RECIEN_PROMOVIDO"
    AUN_NO_HABILITADO = "AUN_NO_HABILITADO"
    PROXIMO_A_HABILITARSE = "PROXIMO_A_HABILITARSE"
    HABILITADO_ORIENTATIVAMENTE = "HABILITADO_ORIENTATIVAMENTE"
    TIEMPO_EXCEDIDO = "TIEMPO_EXCEDIDO"


ESTADOS_HABILITACION = {
    EstadoHabilitacion.SIN_DATOS: {
        "label": "Sin datos suficientes",
        "color": "slate",
        "classes": "border-slate-200 bg-slate-50 text-slate-700",
        "badge_classes": "border-slate-200 bg-white text-slate-700",
    },
    EstadoHabilitacion.SIN_PROXIMO_CINTURON: {
        "label": "Meta avanzada",
        "color": "slate",
        "classes": "border-slate-800 bg-slate-950 text-white",
        "badge_classes": "border-slate-700 bg-slate-900 text-white",
    },
    EstadoHabilitacion.RECIEN_PROMOVIDO: {
        "label": "Recién promovido",
        "color": "blue",
        "classes": "border-blue-200 bg-blue-50 text-blue-900",
        "badge_classes": "border-blue-200 bg-blue-100 text-blue-800",
    },
    EstadoHabilitacion.AUN_NO_HABILITADO: {
        "label": "Aún no habilitado",
        "color": "amber",
        "classes": "border-amber-200 bg-amber-50 text-amber-900",
        "badge_classes": "border-amber-200 bg-amber-100 text-amber-800",
    },
    EstadoHabilitacion.PROXIMO_A_HABILITARSE: {
        "label": "Próximo a habilitarse",
        "color": "orange",
        "classes": "border-orange-200 bg-orange-50 text-orange-900",
        "badge_classes": "border-orange-200 bg-orange-100 text-orange-800",
    },
    EstadoHabilitacion.HABILITADO_ORIENTATIVAMENTE: {
        "label": "Habilitado orientativamente",
        "color": "green",
        "classes": "border-green-200 bg-green-50 text-green-900",
        "badge_classes": "border-green-200 bg-green-100 text-green-800",
    },
    EstadoHabilitacion.TIEMPO_EXCEDIDO: {
        "label": "Tiempo excedido",
        "color": "red",
        "classes": "border-red-200 bg-red-50 text-red-900",
        "badge_classes": "border-red-200 bg-red-100 text-red-800",
    },
}


@dataclass(frozen=True)
class TiempoOrientativo:
    meses_minimos: int
    meses_maximos: int | None = None
    descripcion: str = ""

    @property
    def dias_minimos(self):
        return round(self.meses_minimos * DIAS_MES_REFERENCIA)

    @property
    def dias_maximos(self):
        if self.meses_maximos is None:
            return None
        return round(self.meses_maximos * DIAS_MES_REFERENCIA)


TIEMPOS_ORIENTATIVOS_POR_CINTURON = {
    ("GUP", 10): TiempoOrientativo(3, descripcion="3 meses"),
    ("GUP", 9): TiempoOrientativo(3, descripcion="3 meses"),
    ("GUP", 8): TiempoOrientativo(3, descripcion="3 meses"),
    ("GUP", 7): TiempoOrientativo(3, descripcion="3 meses"),
    ("GUP", 6): TiempoOrientativo(4, descripcion="4 meses"),
    ("GUP", 5): TiempoOrientativo(4, descripcion="4 meses"),
    ("GUP", 4): TiempoOrientativo(5, descripcion="5 meses"),
    ("GUP", 3): TiempoOrientativo(5, descripcion="5 meses"),
    ("GUP", 2): TiempoOrientativo(6, descripcion="6 meses"),
    ("GUP", 1): TiempoOrientativo(6, 12, "6 a 12 meses"),
}


GLOSARIO_TIEMPOS_ORIENTATIVOS = [
    {
        "tipo_rango": "GUP",
        "numeracion": 10,
        "nombre": "Blanco",
        "grado": "10° gup",
        "tiempo": "3 meses",
        "acumulado": "0–3 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 9,
        "nombre": "Punta Amarilla",
        "grado": "9° gup",
        "tiempo": "3 meses",
        "acumulado": "3–6 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 8,
        "nombre": "Amarillo",
        "grado": "8° gup",
        "tiempo": "3 meses",
        "acumulado": "6–9 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 7,
        "nombre": "Punta Verde",
        "grado": "7° gup",
        "tiempo": "3 meses",
        "acumulado": "9–12 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 6,
        "nombre": "Verde",
        "grado": "6° gup",
        "tiempo": "4 meses",
        "acumulado": "12–16 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 5,
        "nombre": "Punta Azul",
        "grado": "5° gup",
        "tiempo": "4 meses",
        "acumulado": "16–20 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 4,
        "nombre": "Azul",
        "grado": "4° gup",
        "tiempo": "5 meses",
        "acumulado": "20–25 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 3,
        "nombre": "Punta Roja",
        "grado": "3° gup",
        "tiempo": "5 meses",
        "acumulado": "25–30 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 2,
        "nombre": "Rojo",
        "grado": "2° gup",
        "tiempo": "6 meses",
        "acumulado": "30–36 meses",
    },
    {
        "tipo_rango": "GUP",
        "numeracion": 1,
        "nombre": "Punta Negra",
        "grado": "1° gup",
        "tiempo": "6 a 12 meses",
        "acumulado": "36–42/48 meses",
    },
    {
        "tipo_rango": "DAN",
        "numeracion": 1,
        "nombre": "1° Dan",
        "grado": "1° dan",
        "tiempo": "Meta estimada",
        "acumulado": "3,5 a 4 años desde el inicio",
    },
]
