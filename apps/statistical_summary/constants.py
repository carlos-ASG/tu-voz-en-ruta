"""
Constantes y configuraciones para statistical_summary.

Este módulo centraliza todas las constantes usadas en el cálculo
de estadísticas para facilitar mantenimiento y configuración.
"""
import pytz

# Timezone para conversión de fechas (visual en admin, DB usa UTC)
# Hardcodeado aquí porque es específico para la visualización de stats,
# no para el almacenamiento en DB que siempre usa UTC
DISPLAY_TIMEZONE = pytz.timezone("America/Mazatlan")

# Límites de visualización
MAX_UNITS_IN_CHART = 10

# Labels de períodos
PERIOD_LABELS = {
    "today": "Hoy",
    "week": "Esta Semana",
    "month": "Este Mes",
    "year": "Este Año",
    "all": "Todo el Tiempo",
}

# Labels de tipos de preguntas
QUESTION_TYPE_LABELS = {
    "RATING": "calificación",
    "CHOICE": "opción",
    "MULTI_CHOICE": "múltiples opciones",
}
