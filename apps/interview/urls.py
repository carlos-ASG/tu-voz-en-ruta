from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    # Vista de agradecimiento (debe ir ANTES del patrón dinámico)
    path('thank-you/', views.thank_you, name='thank_you'),

    # Vista para seleccionar unidad (acceso desde admin panel)
    path('', views.select_unit_for_survey, name='select_unit'),

    # Formulario de encuesta para una unidad específica (basado en transit_number)
    path('<str:transit_number>/', views.survey_form, name='survey_form'),

    # Envío del formulario (procesa todos los formularios)
    path('<str:transit_number>/submit/', views.submit_survey, name='submit_survey'),
]
