from django.db import models
from interview.models import SurveySubmission


class StatisticalSummary(SurveySubmission):
    """
    Modelo proxy para acceder al dashboard de estadísticas desde el admin.
    Hereda de SurveySubmission pero no crea una tabla nueva.
    """
    class Meta:
        proxy = True
        verbose_name = "Dashboard de Estadísticas"
        verbose_name_plural = "Dashboard de Estadísticas"
        # Desactivar permisos por defecto para evitar conflictos con el modelo base
        default_permissions = ()  # No crear permisos add, change, delete, view