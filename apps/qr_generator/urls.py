from django.urls import path
from . import views

app_name = 'qr_generator'

urlpatterns = [
    path('', views.qr_generator_view, name='qr_generator'),
    path('generate/', views.generate_qr_codes, name='generate_qr_codes'),
]
