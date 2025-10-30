# tu_proyecto/urls_public.py
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    # El admin del esquema PÚBLICO
    path('super-admin/', admin.site.urls),  
    
    # La vista de selección de organización
    path('', include('organization.urls', namespace='organization')),
]