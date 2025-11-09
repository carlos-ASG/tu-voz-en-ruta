from django.contrib import admin
from django.shortcuts import redirect

from .models import StatisticalSummary
from apps.transport.admin import tenant_admin_site


class StatisticalSummaryAdmin(admin.ModelAdmin):
    """
    Admin para el modelo proxy StatisticalSummary.
    Redirige a la vista de estadísticas del dashboard.
    """
    
    def has_add_permission(self, request):
        """No permitir agregar nuevos registros (es un modelo proxy)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros (es un modelo proxy)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros (es un modelo proxy)"""
        return False
    
    def changelist_view(self, request, extra_context=None):
        """
        Sobrescribir la vista de listado para redirigir al dashboard de estadísticas.
        """
        # Redirigir a la vista de estadísticas usando URL absoluta
        # No usar reverse() porque tenant_admin_site no tiene acceso al namespace
        dashboard_url = '/statistical-summary/dashboard/'
        return redirect(dashboard_url)


# Registrar en AMBOS sitios de admin
tenant_admin_site.register(StatisticalSummary, StatisticalSummaryAdmin)  # Admin personalizado


