"""
Utilidades para manejo de fechas y períodos.

Este módulo contiene funciones puras para calcular rangos de fechas
basados en períodos definidos (hoy, semana, mes, año, todo).
"""
from datetime import datetime, timedelta
from django.utils import timezone

from ..constants import DISPLAY_TIMEZONE, PERIOD_LABELS
from ..schemas import PeriodType


def get_period_date_range(period: PeriodType) -> tuple[datetime | None, str]:
    """
    Obtiene el rango de fechas y label según el período.
    
    Convierte la hora UTC actual a la zona horaria local configurada
    (DISPLAY_TIMEZONE) y calcula el inicio del período solicitado.
    
    Args:
        period: Período a filtrar ("today", "week", "month", "year", "all")
        
    Returns:
        Tupla con (start_date, period_label)
        - start_date: Fecha de inicio en timezone local (None para "all")
        - period_label: Etiqueta legible del período
        
    Raises:
        ValueError: Si period no es válido
        
    Example:
        >>> start, label = get_period_date_range("today")
        >>> print(label)
        "Hoy"
        >>> start, label = get_period_date_range("all")
        >>> assert start is None
        >>> print(label)
        "Todo el Tiempo"
    """
    # Validación
    if period not in PERIOD_LABELS:
        raise ValueError(
            f"Invalid period: {period}. "
            f"Must be one of: {', '.join(PERIOD_LABELS.keys())}"
        )
    
    # Obtener hora actual en UTC y convertir a hora local
    now_utc: datetime = timezone.now()
    now_local: datetime = now_utc.astimezone(DISPLAY_TIMEZONE)
    
    # Calcular fecha de inicio según período
    start_date: datetime | None
    
    match period:
        case "today":
            # Inicio del día en hora local
            start_date = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        
        case "week":
            # Lunes de esta semana en hora local
            start_date = now_local - timedelta(days=now_local.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        case "month":
            # Primer día del mes en hora local
            start_date = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        case "year":
            # Primer día del año en hora local
            start_date = now_local.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
        
        case "all":
            # Sin filtro de fecha
            start_date = None
    
    period_label = PERIOD_LABELS[period]
    
    return start_date, period_label
