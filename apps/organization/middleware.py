from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from django_tenants.utils import get_tenant_model

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


class TenantActiveMiddleware(MiddlewareMixin):
    """
    Middleware que verifica si el tenant actual está activo.
    Si el tenant no está activo, redirige a una página de organización inactiva.

    También agrega contexto de tenant a Sentry para facilitar debugging multi-tenant.
    """

    def process_request(self, request):
        # Obtener el tenant actual desde el request (configurado por TenantMainMiddleware)
        tenant = getattr(request, 'tenant', None)

        if tenant is None:
            # Si no hay tenant, no hacer nada (probablemente estamos en el esquema público)
            return None

        # Agregar contexto de tenant a Sentry para identificar errores por organización
        if SENTRY_AVAILABLE and tenant.schema_name != 'public':
            sentry_sdk.set_tag("tenant_schema", tenant.schema_name)
            sentry_sdk.set_tag("tenant_name", tenant.name)
            sentry_sdk.set_tag("tenant_active", tenant.is_active)
            sentry_sdk.set_context("tenant", {
                "id": str(tenant.id),
                "name": tenant.name,
                "schema": tenant.schema_name,
                "domain": request.get_host(),
                "is_active": tenant.is_active,
            })

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
