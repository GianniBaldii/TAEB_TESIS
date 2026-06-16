from django import template

from apps.alumnos.models import Examen

register = template.Library()


NEUTRAL_THEME = {
    "container": "border-slate-200 bg-slate-50 text-slate-800",
    "badge": "border-slate-300 bg-white text-slate-700",
    "accent": "bg-slate-400",
}

BELT_THEMES = {
    ("GUP", 10): {
        "container": "border-slate-200 bg-white text-slate-900",
        "badge": "border-slate-300 bg-white text-slate-900",
        "accent": "bg-white ring-1 ring-slate-300",
    },
    ("GUP", 9): {
        "container": "border-yellow-300 bg-white text-slate-900",
        "badge": "border-yellow-300 bg-white text-slate-900",
        "accent": "bg-yellow-400",
    },
    ("GUP", 8): {
        "container": "border-yellow-400 bg-yellow-50 text-yellow-950",
        "badge": "border-yellow-400 bg-yellow-300 text-yellow-950",
        "accent": "bg-yellow-400",
    },
    ("GUP", 7): {
        "container": "border-green-400 bg-yellow-50 text-slate-900",
        "badge": "border-green-500 bg-yellow-300 text-slate-950",
        "accent": "bg-green-500",
    },
    ("GUP", 6): {
        "container": "border-green-500 bg-green-50 text-green-950",
        "badge": "border-green-500 bg-green-500 text-white",
        "accent": "bg-green-700",
    },
    ("GUP", 5): {
        "container": "border-blue-400 bg-green-50 text-slate-900",
        "badge": "border-blue-500 bg-green-500 text-white",
        "accent": "bg-blue-600",
    },
    ("GUP", 4): {
        "container": "border-blue-500 bg-blue-50 text-blue-950",
        "badge": "border-blue-500 bg-blue-600 text-white",
        "accent": "bg-blue-800",
    },
    ("GUP", 3): {
        "container": "border-red-400 bg-blue-50 text-slate-900",
        "badge": "border-red-500 bg-blue-600 text-white",
        "accent": "bg-red-500",
    },
    ("GUP", 2): {
        "container": "border-red-500 bg-red-50 text-red-950",
        "badge": "border-red-500 bg-red-600 text-white",
        "accent": "bg-red-800",
    },
    ("GUP", 1): {
        "container": "border-slate-900 bg-red-50 text-slate-950",
        "badge": "border-slate-900 bg-red-600 text-white",
        "accent": "bg-slate-950",
    },
}

DAN_THEME = {
    "container": "border-yellow-500 bg-slate-950 text-white",
    "badge": "border-yellow-400 bg-yellow-300 text-slate-950",
    "accent": "bg-yellow-400",
}

ESTADO_THEMES = {
    Examen.Estado.PENDIENTE: "border-yellow-200 bg-yellow-50 text-yellow-800",
    Examen.Estado.APROBADO: "border-green-200 bg-green-50 text-green-800",
    Examen.Estado.DESAPROBADO: "border-red-200 bg-red-50 text-red-800",
    Examen.Estado.AUSENTE: "border-orange-200 bg-orange-50 text-orange-800",
    Examen.Estado.ANULADO: "border-slate-200 bg-slate-100 text-slate-600",
}


@register.filter
def belt_theme(cinturon):
    if not cinturon:
        return NEUTRAL_THEME
    if cinturon.tipo_rango == "DAN":
        return DAN_THEME
    return BELT_THEMES.get((cinturon.tipo_rango, cinturon.numeracion), NEUTRAL_THEME)


@register.filter
def examen_estado_theme(estado):
    return ESTADO_THEMES.get(estado, ESTADO_THEMES[Examen.Estado.PENDIENTE])
