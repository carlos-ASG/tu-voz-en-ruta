"""
Service para lógica de negocio de encuestas.

Este módulo contiene la lógica de negocio relacionada con envíos
de encuestas, delegando el acceso a datos al repository correspondiente.
"""
from typing import Any

from ..repositories import survey_repository
from ..schemas import TimelineData


def get_submission_total(filters: dict[str, Any]) -> int:
    """
    Obtiene el total de envíos de encuestas.
    
    Args:
        filters: Filtros para queryset
        
    Returns:
        Número total de envíos
        
    Example:
        >>> total = get_submission_total({'unit_id': 'uuid'})
        >>> print(f"Total submissions: {total}")
        Total submissions: 42
    """
    return survey_repository.get_submission_count(filters)


def get_timeline_data(
    filters: dict[str, Any],
    group_by_hour: bool = False
) -> TimelineData:
    """
    Obtiene timeline de envíos.
    
    Args:
        filters: Filtros para queryset
        group_by_hour: True para agrupar por hora (período "today"),
                      False para agrupar por día
        
    Returns:
        TimelineData con fechas y conteos
        
    Example:
        >>> timeline = get_timeline_data({'unit_id': 'uuid'}, group_by_hour=True)
        >>> for date, count in zip(timeline.dates, timeline.counts):
        ...     print(f"{date}: {count} envíos")
        00:00: 2 envíos
        01:00: 5 envíos
        02:00: 3 envíos
    """
    return survey_repository.get_submissions_timeline(filters, group_by_hour)
