# organization/urls.py
# URLs para el esquema PÚBLICO (dominio principal sin subdominio)
from django.urls import path
from django.contrib import admin

from organization.views import select_organization, index

app_name = 'organization'

urlpatterns = [
    path('', select_organization, name='select_organization'),
]