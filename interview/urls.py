from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    # Paso 1: Seleccionar unidad (sin organización - muestra todas)
    path('', views.select_unit, name='select_unit'),
    
    # Paso 2: Formulario de encuesta con organización y unidad
    path('<uuid:organization_id>/<uuid:unit_id>/', views.survey_form, name='survey_form'),
    
    # Envío del formulario
    path('<uuid:organization_id>/<uuid:unit_id>/submit/', views.submit_survey, name='submit_survey'),
    
    # Vista de agradecimiento
    path('thank-you/', views.thank_you, name='thank_you'),
]
