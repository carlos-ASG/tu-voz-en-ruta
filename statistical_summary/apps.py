from django.apps import AppConfig


class StatisticalSummaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'statistical_summary'
    verbose_name = 'Resumen Estadístico'  # Esto controla el nombre en el sidebar
