from calendar import c
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from statistical_summary.utils import calculate_statistics, get_units_and_routes

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "statistical_summary/statistics_dashboard.html" # Tu template de gráficas
    """
    Vista de dashboard de estadísticas personalizada.
    
    Filtros aplicados:
    1. Organización del usuario autenticado (CRÍTICO)
    2. Período de fechas (hoy, semana, mes, año, todo)
    """
    
    # FILTRO CRÍTICO: Obtener organización desde el tenant actual
    def get_context_data(self, **kwargs):
        # Obtener organización desde el tenant (django-tenants middleware)
        user_organization = self.request.tenant
        
        if not user_organization:
            # Si no hay tenant, mostrar página de error
            context = {
                'error_message': 'No se pudo determinar la organización. Verifica que estés accediendo desde el dominio correcto.',
                'has_data': False,
            }
            return context

        # Obtener período de filtro desde parámetros GET
        period = self.request.GET.get('period', 'today')
        
        # Obtener filtros opcionales de ruta o unidad
        route_id = self.request.GET.get('route', None)
        unit_id = self.request.GET.get('unit', None)
        
        # Si ambos están presentes, priorizar ruta y limpiar unidad
        if route_id and unit_id:
            unit_id = None

        # Calcular estadísticas con filtros (sin organization, el schema filtra)
        statistics = calculate_statistics(
            period=period,
            route_id=route_id,
            unit_id=unit_id
        )
        
        # Obtener rutas y unidades para los selectores (sin organization, el schema filtra)
        filters_data = get_units_and_routes()
        
        context = {
            'has_data': bool(statistics),
            'period': period,
            'organization_name': user_organization.name,
            'routes': filters_data['routes'],
            'units': filters_data['units'],
            'selected_route': route_id,
            'selected_unit': unit_id,
            **statistics,
        }
        
        return context