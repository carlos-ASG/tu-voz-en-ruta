from django.urls import include, path
from apps.transport.admin import tenant_admin_site

urlpatterns = [
    # Admin personalizado para el tenant
    path('admin/', tenant_admin_site.urls),

    # App de encuestas (accesible vía /survey/)
    path('survey/', include('apps.interview.urls')),

    # Dashboard de estadísticas
    path('statistical-summary/', include('apps.statistical_summary.urls')),

    # Generador de códigos QR
    path('qr-generator/', include('apps.qr_generator.urls')),
] 