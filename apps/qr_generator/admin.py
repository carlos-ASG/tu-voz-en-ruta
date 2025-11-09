from django.contrib import admin
from django.shortcuts import redirect

from apps.qr_generator.models import QrGenerator
from apps.transport.admin import tenant_admin_site


class QrGeneratorAdmin(admin.ModelAdmin):
    """
    Admin para el modelo proxy QrGenerator.
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
        qr_generator_url = '/qr-generator/'
        return redirect(qr_generator_url)


# Registrar en AMBOS sitios de admin
tenant_admin_site.register(QrGenerator, QrGeneratorAdmin)  # Admin personalizado