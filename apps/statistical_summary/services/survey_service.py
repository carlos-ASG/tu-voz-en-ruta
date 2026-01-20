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


def get_submissions_by_unit_data(filters: dict[str, Any]) -> dict[str, int]:
    """
    Obtiene formularios agrupados por unidad.
    
    Delega al repository para obtener la agrupación.
    
    Args:
        filters: Filtros para queryset
        
    Returns:
        Diccionario {transit_number: count}
        
    Example:
        >>> by_unit = get_submissions_by_unit_data({})
        >>> for unit, count in by_unit.items():
        ...     print(f"Unidad {unit}: {count} formularios")
        Unidad ABC123: 15 formularios
        Unidad XYZ789: 10 formularios
    """
    return survey_repository.get_submissions_by_unit(filters)
