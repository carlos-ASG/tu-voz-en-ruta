"""
Utilidades para construcción de filtros de queries.

Este módulo contiene funciones para construir diccionarios de filtros
que se aplican a los querysets de Django ORM.
"""
from datetime import datetime
from typing import Any


def build_submission_filters(
    start_date: datetime | None,
    route_id: str | None,
    unit_id: str | None
) -> dict[str, Any]:
    """
    Construye filtros para SurveySubmission queryset.
    
    Los filtros son mutuamente excluyentes: si se proporciona route_id,
    se ignora unit_id. Esto permite filtrar por toda una ruta o por
    una unidad específica.
    
    Args:
        start_date: Fecha mínima de submitted_at (None = sin filtro de fecha)
        route_id: ID de ruta para filtrar (None = sin filtro de ruta)
        unit_id: ID de unidad para filtrar (None = sin filtro de unidad)
        
    Returns:
        Diccionario de filtros para SurveySubmission.objects.filter(**filters)
        
    Example:
        >>> from datetime import datetime
        >>> filters = build_submission_filters(
        ...     start_date=datetime(2024, 1, 1),
        ...     route_id="uuid-route",
        ...     unit_id=None
        ... )
        >>> print(filters)
        {'submitted_at__gte': datetime(2024, 1, 1, 0, 0), 'unit__route_id': 'uuid-route'}
    """
    filters: dict[str, Any] = {}
    
    if start_date:
        filters['submitted_at__gte'] = start_date
    
    # Filtros mutuamente excluyentes
    if route_id:
        filters['unit__route_id'] = route_id
    elif unit_id:
        filters['unit_id'] = unit_id
    
    return filters


def build_complaint_filters(
    start_date: datetime | None,
    route_id: str | None,
    unit_id: str | None
) -> dict[str, Any]:
    """
    Construye filtros para Complaint queryset.
    
    Idéntico a build_submission_filters pero para el modelo Complaint.
    Los campos de fecha y relaciones son los mismos en ambos modelos.
    
    Args:
        start_date: Fecha mínima de submitted_at (None = sin filtro de fecha)
        route_id: ID de ruta para filtrar (None = sin filtro de ruta)
        unit_id: ID de unidad para filtrar (None = sin filtro de unidad)
        
    Returns:
        Diccionario de filtros para Complaint.objects.filter(**filters)
        
    Example:
        >>> filters = build_complaint_filters(None, None, "uuid-unit")
        >>> print(filters)
        {'unit_id': 'uuid-unit'}
    """
    filters: dict[str, Any] = {}
    
    if start_date:
        filters['submitted_at__gte'] = start_date
    
    # Filtros mutuamente excluyentes
    if route_id:
        filters['unit__route_id'] = route_id
    elif unit_id:
        filters['unit_id'] = unit_id
    
    return filters
