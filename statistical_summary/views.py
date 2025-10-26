from calendar import c
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from statistical_summary.utils import calculate_statistics

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

        statistics = calculate_statistics(period=period, organization=user_organization)
        
        context = {
            'has_data': bool(statistics),
            'period': period,
            'organization_name': user_organization.name,
            **statistics,
            }
        
        return context