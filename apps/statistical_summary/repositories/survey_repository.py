"""
Repository para operaciones de SurveySubmission.

Este módulo encapsula todas las queries relacionadas con el modelo
SurveySubmission, proporcionando una API limpia para la capa de servicios.
"""
from typing import Any
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour

from apps.interview.models.survey_submission import SurveySubmission
from ..schemas import TimelineData


def get_submission_count(filters: dict[str, Any]) -> int:
    """
    Obtiene el conteo total de envíos con filtros.
    
    Args:
        filters: Filtros a aplicar al queryset
        
    Returns:
        Número total de envíos que cumplen los filtros
        
    Example:
        >>> count = get_submission_count({'unit_id': 'uuid-here'})
        >>> print(count)
        42
    """
    return SurveySubmission.objects.filter(**filters).count()


def get_submissions_timeline(
    filters: dict[str, Any],
    group_by_hour: bool = False
) -> TimelineData:
    """
    Obtiene timeline de envíos agrupados por fecha u hora.
    
    Args:
        filters: Filtros a aplicar al queryset
        group_by_hour: True para agrupar por hora, False por día
        
    Returns:
        TimelineData con listas de fechas y conteos
        
    Example:
        >>> timeline = get_submissions_timeline(
        ...     {'unit_id': 'uuid'},
        ...     group_by_hour=True
        ... )
        >>> print(timeline.dates)
        ['00:00', '01:00', '02:00', ...]
        >>> print(timeline.counts)
        [5, 3, 8, ...]
    """
    # Seleccionar función de truncado según granularidad
    if group_by_hour:
        submissions_by_time = (
            SurveySubmission.objects.filter(**filters)
            .annotate(time=TruncHour('submitted_at'))
            .values('time')
            .annotate(count=Count('id'))
            .order_by('time')
        )
    else:
        submissions_by_time = (
            SurveySubmission.objects.filter(**filters)
            .annotate(time=TruncDate('submitted_at'))
            .values('time')
            .annotate(count=Count('id'))
            .order_by('time')
        )
    
    # Separar en listas de fechas y conteos
    dates: list[str] = []
    counts: list[int] = []
    
    for item in submissions_by_time:
        time_obj = item.get('time')
        if time_obj:
            if group_by_hour:
                # Formato: 'HH:00'
                dates.append(time_obj.strftime('%H:00'))
            else:
                # Formato: 'YYYY-MM-DD'
                dates.append(time_obj.strftime('%Y-%m-%d'))
            counts.append(item.get('count', 0))
    
    return TimelineData(dates=dates, counts=counts)


def get_submissions_by_unit(filters: dict[str, Any]) -> dict[str, int]:
    """
    Obtiene envíos de formularios agrupados por número de tránsito.
    
    Similar a complaint_repository.get_by_unit() pero para SurveySubmission.
    Retorna diccionario ordenado descendentemente por cantidad de envíos.
    
    Args:
        filters: Filtros a aplicar al queryset
        
    Returns:
        Diccionario {transit_number: count} ordenado por cantidad descendente
        
    Example:
        >>> by_unit = get_submissions_by_unit({})
        >>> print(by_unit)
        {'ABC123': 15, 'XYZ789': 10, 'DEF456': 5}
    """
    # Filtrar envíos y agrupar por unidad
    submissions_by_unit = (
        SurveySubmission.objects.filter(**filters)
        .exclude(unit__isnull=True)  # Excluir envíos sin unidad
        .values('unit__transit_number')
        .annotate(count=Count('id'))
        .order_by('-count')  # Ordenar descendente por cantidad
    )
    
    # Convertir a diccionario simple: {transit_number: count}
    by_unit: dict[str, int] = {}
    for item in submissions_by_unit:
        transit_number = item.get('unit__transit_number')
        count = item.get('count', 0)
        if transit_number:
            by_unit[transit_number] = count
    
    return by_unit
