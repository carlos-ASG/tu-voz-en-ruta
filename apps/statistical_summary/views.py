"""
Views para statistical_summary.

Este módulo contiene las vistas CBV para el dashboard de estadísticas,
delegando toda la lógica de negocio a los services.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from typing import Any

from .services.statistics_service import calculate_dashboard_statistics
from .repositories.transport_repository import get_filter_data
from .schemas import PeriodType


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Vista de dashboard de estadísticas.
    
    Requiere:
        - Usuario autenticado (LoginRequiredMixin)
        - Permiso 'can_view_statistical_dashboard'
    
    Filtros soportados (GET params):
        - period: "today" | "week" | "month" | "year" | "all" (default: "today")
        - route: UUID de ruta
        - unit: UUID de unidad (mutuamente excluyente con route)
    
    Template:
        statistical_summary/statistics_dashboard.html
    """
    template_name = "statistical_summary/statistics_dashboard.html"
    permission_required = 'statistical_summary.can_view_statistical_dashboard'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Prepara el contexto con todas las estadísticas del dashboard.
        
        Returns:
            Diccionario con datos para el template
        """
        context = super().get_context_data(**kwargs)
        
        # Validar tenant (django-tenants middleware)
        if not self.request.tenant:
            return {
                'error_message': 'No se pudo determinar la organización. '
                                'Verifica que estés accediendo desde el dominio correcto.',
                'has_data': False,
            }
        
        # Obtener parámetros de filtro desde GET
        period: PeriodType = self.request.GET.get('period', 'today')  # type: ignore
        route_id = self.request.GET.get('route')
        unit_id = self.request.GET.get('unit')
        
        # Si ambos filtros están presentes, priorizar ruta y limpiar unidad
        if route_id and unit_id:
            unit_id = None
        
        try:
            # Calcular estadísticas usando el service principal
            statistics = calculate_dashboard_statistics(period, route_id, unit_id)
            
            # Obtener datos para los filtros (rutas y unidades)
            filters_data = get_filter_data()
            
            # Preparar contexto para el template
            # Nota: El filtro custom 'tojson' en el template se encargará de
            # serializar los datos a JSON, eliminando duplicación.
            context.update({
                'has_data': True,
                'period': period,
                'organization_name': self.request.tenant.name,
                'selected_route': route_id,
                'selected_unit': unit_id,
                # Objeto completo con todas las estadísticas
                'statistics': statistics,
                # Datos para filtros (rutas y unidades)
                'filters_data': filters_data,
            })
        
        except ValueError as e:
            # Manejar período inválido u otros errores de validación
            context.update({
                'error_message': f'Error en los parámetros: {str(e)}',
                'has_data': False,
            })
        
        except Exception as e:
            # Manejar cualquier otro error inesperado
            context.update({
                'error_message': f'Error al calcular estadísticas: {str(e)}',
                'has_data': False,
            })
        
        return context
