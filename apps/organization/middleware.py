from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant_model


class TenantActiveMiddleware(MiddlewareMixin):
    """
    Middleware que verifica si el tenant actual está activo.
    Si el tenant no está activo, redirige a una página de organización inactiva.
    """

    def process_request(self, request):
        # Obtener el tenant actual desde el request (configurado por TenantMainMiddleware)
        tenant = getattr(request, 'tenant', None)

        if tenant is None:
            # Si no hay tenant, no hacer nada (probablemente estamos en el esquema público)
            return None

        # Verificar si es el tenant público (esquema 'public')
        if tenant.schema_name == 'public':
            # No verificar el estado del tenant público
            return None

        # Verificar si el tenant está activo
        if not tenant.is_active:
            # Renderizar la plantilla de organización inactiva
            return render(request, 'organization/organization_inactive.html', {
                'organization_name': tenant.name,
                'tenant': tenant,
            }, status=503)  # 503 Service Unavailable

        # Si el tenant está activo, continuar con la solicitud normalmente
        return None
