# tu_proyecto/urls_public.py
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # El admin del esquema PÚBLICO
    path('super-admin/', admin.site.urls),

    # La vista de selección de organización
    path('', include('apps.organization.urls', namespace='organization')),

    # Health checks - disponibles en esquema público para monitoreo
    path('health/', include('health_check.urls')),
    path('monitoring/', include('monitoring.urls', namespace='monitoring')),
]