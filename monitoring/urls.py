from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('sentry-debug/', views.trigger_error),
]