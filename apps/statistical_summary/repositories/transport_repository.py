"""
Repository para operaciones de Route y Unit.

Este módulo encapsula las queries relacionadas con rutas y unidades,
principalmente para obtener datos de filtros del dashboard.
"""
from apps.transport.models import Route, Unit
from ..schemas import FilterData, RouteData, UnitData


def get_filter_data() -> FilterData:
    """
    Obtiene rutas y unidades para filtros del dashboard.
    
    El aislamiento por organización es automático vía schema del tenant.
    
    Returns:
        FilterData con listas de rutas y unidades ordenadas
        
    Example:
        >>> filter_data = get_filter_data()
        >>> print(len(filter_data.routes))
        5
        >>> print(filter_data.routes[0].name)
        'Ruta Centro-Norte'
        >>> print(len(filter_data.units))
        20
        >>> print(filter_data.units[0].transit_number)
        'ABC123'
    """
    # Obtener rutas ordenadas por nombre
    routes = Route.objects.order_by('name').values('id', 'name')
    
    # Obtener unidades ordenadas por número de tránsito
    units = Unit.objects.order_by('transit_number').values('id', 'transit_number')
    
    return FilterData(
        routes=[RouteData(id=str(route['id']), name=route['name']) for route in routes],
        units=[UnitData(id=str(unit['id']), transit_number=unit['transit_number']) for unit in units]
    )
