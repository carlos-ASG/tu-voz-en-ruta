"""
Service para lógica de negocio de quejas.

Este módulo contiene la lógica de negocio relacionada con quejas,
delegando el acceso a datos al repository correspondiente.
"""
from typing import Any

from ..repositories import complaint_repository
from ..schemas import ComplaintsSummary


def get_complaints_data(filters: dict[str, Any]) -> ComplaintsSummary:
    """
    Obtiene datos completos de quejas.
    
    Args:
        filters: Filtros para queryset
        
    Returns:
        ComplaintsSummary con total y distribución por motivo
        
    Example:
        >>> summary = get_complaints_data({'unit_id': 'uuid'})
        >>> print(f"Total: {summary.total_complaints}")
        Total: 42
        >>> for reason, count in summary.by_reason.items():
        ...     print(f"{reason}: {count}")
        Mal servicio: 20
        Llegada tardía: 15
        Vehículo sucio: 7
    """
    return complaint_repository.get_summary(filters)


def get_complaints_by_unit_data(filters: dict[str, Any]) -> dict[str, int]:
    """
    Obtiene quejas agrupadas por unidad.
    
    Args:
        filters: Filtros para queryset
        
    Returns:
        Diccionario {transit_number: count}
        
    Example:
        >>> by_unit = get_complaints_by_unit_data({})
        >>> for unit, count in by_unit.items():
        ...     print(f"Unidad {unit}: {count} quejas")
        Unidad ABC123: 5 quejas
        Unidad XYZ789: 3 quejas
    """
    return complaint_repository.get_by_unit(filters)
