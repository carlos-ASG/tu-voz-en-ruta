from django.contrib import admin
from django.shortcuts import redirect

from apps.qr_generator.models import QrGenerator
from apps.transport.admin import tenant_admin_site


class QrGeneratorAdmin(admin.ModelAdmin):
    """
    Admin para el modelo proxy QrGenerator.
    Redirige a la vista del generador de códigos QR.

    Permisos:
    - Solo usuarios con 'can_generate_qr_codes' pueden acceder
    - No permite add, change ni delete (es un modelo proxy de solo lectura)
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

    def has_view_permission(self, request, obj=None):
        """
        Permitir acceso solo a usuarios con el permiso personalizado.
        Este permiso controla la visibilidad en el menú del admin.
        """
        return request.user.has_perm('qr_generator.can_generate_qr_codes')
    
    def changelist_view(self, request, extra_context=None):
        """
        Sobrescribir la vista de listado para redirigir al generador de QR.
        """
        # Redirigir a la vista de generación de QR usando URL absoluta
        # No usar reverse() porque tenant_admin_site no tiene acceso al namespace
        qr_generator_url = '/qr-generator/'
        return redirect(qr_generator_url)


# Registrar en el sitio de admin personalizado del tenant
tenant_admin_site.register(QrGenerator, QrGeneratorAdmin)