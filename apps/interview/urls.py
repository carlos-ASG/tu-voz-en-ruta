from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    # Formulario de encuesta
    path('', views.survey_form, name='survey_form'),
    
    # Envío del formulario (procesa todos los formularios)
    path('submit/', views.submit_survey, name='submit_survey'),

    # Vista de agradecimiento
    path('thank-you/', views.thank_you, name='thank_you'),
]
