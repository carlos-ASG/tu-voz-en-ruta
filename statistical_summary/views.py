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
    
    # FILTRO CRÍTICO: Obtener organización del usuario
    def get_context_data(self, **kwargs):
        user_organization = self.request.user.organization
        
        if not user_organization:
            # Si el usuario no tiene organización asignada, mostrar página vacía
            context = {
                'error_message': 'Tu usuario no tiene una organización asignada. Contacta al administrador.',
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

        # Calcular estadísticas con filtros
        statistics = calculate_statistics(
            period=period, 
            organization=user_organization,
            route_id=route_id,
            unit_id=unit_id
        )
        
        # Obtener rutas y unidades para los selectores
        filters_data = get_units_and_routes(user_organization)
        
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