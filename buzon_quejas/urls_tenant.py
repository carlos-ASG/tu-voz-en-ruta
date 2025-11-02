from django.urls import include, path
from transport.admin import tenant_admin_site

urlpatterns = [
    # Admin personalizado para el tenant
    path('admin/', tenant_admin_site.urls),
    
    # App de encuestas
    path('interview/', include('interview.urls')),
    
    # Dashboard de estadísticas
    path('statistical-summary/', include('statistical_summary.urls')),
    
    # Generador de códigos QR
    path('qr-generator/', include('qr_generator.urls')),
] 