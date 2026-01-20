"""
Repository para operaciones de Complaint.

Este módulo encapsula todas las queries relacionadas con el modelo
Complaint, proporcionando funciones para obtener resúmenes y agregaciones.
"""
from typing import Any
from django.db.models import Count

from apps.interview.models.complaint import Complaint
from ..schemas import ComplaintsSummary


def get_complaint_count(filters: dict[str, Any]) -> int:
    """
    Obtiene el conteo total de quejas con filtros.
    
    Args:
        filters: Filtros a aplicar al queryset
        
    Returns:
        Número total de quejas que cumplen los filtros
        
    Example:
        >>> count = get_complaint_count({'unit_id': 'uuid-here'})
        >>> print(count)
        15
    """
    return Complaint.objects.filter(**filters).count()


def get_summary(filters: dict[str, Any]) -> ComplaintsSummary:
    """
    Obtiene resumen de quejas con conteo por motivo.
    
    Args:
        filters: Filtros a aplicar al queryset
        
    Returns:
        ComplaintsSummary con total y distribución por motivo
        
    Example:
        >>> summary = get_summary({'unit_id': 'uuid'})
        >>> print(summary.total_complaints)
        42
        >>> print(summary.by_reason)
        {'Mal servicio': 20, 'Llegada tardía': 15, 'Vehículo sucio': 7}
    """
    qs = Complaint.objects.filter(**filters)
    total_complaints = qs.count()
    
    # Agrupar por motivo de la queja y contar
    reason_counts = (
        qs.values('reason__label')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Convertir a diccionario simple: {motivo: count}
    by_reason: dict[str, int] = {}
    for item in reason_counts:
        label = item.get('reason__label') or 'Sin motivo'
        count = item.get('count', 0)
        by_reason[label] = count
    
    return ComplaintsSummary(
        total_complaints=total_complaints,
        by_reason=by_reason
    )


def get_by_unit(filters: dict[str, Any]) -> dict[str, int]:
    """
    Obtiene quejas agrupadas por número de tránsito.
    
    Args:
        filters: Filtros a aplicar al queryset
        
    Returns:
        Diccionario {transit_number: count} ordenado por cantidad descendente
        
    Example:
        >>> by_unit = get_by_unit({})
        >>> print(by_unit)
        {'ABC123': 5, 'XYZ789': 3, 'DEF456': 1}
    """
    # Filtrar quejas y agrupar por unidad
    complaints_by_unit = (
        Complaint.objects.filter(**filters)
        .exclude(unit__isnull=True)  # Excluir quejas sin unidad asociada
        .values('unit__transit_number')
        .annotate(count=Count('id'))
        .order_by('-count')  # Ordenar por cantidad de quejas (descendente)
    )
    
    # Convertir a diccionario simple: {transit_number: count}
    by_unit: dict[str, int] = {}
    for item in complaints_by_unit:
        transit_number = item.get('unit__transit_number')
        count = item.get('count', 0)
        if transit_number:
            by_unit[transit_number] = count
    
    return by_unit
