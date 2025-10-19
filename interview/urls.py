from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    path('', views.survey_form, name='survey_form'),
    path('submit/', views.submit_survey, name='submit_survey'),
]
