from django.db import models
from apps.interview.models import SurveySubmission


class StatisticalSummary(SurveySubmission):
    """
    Modelo proxy para acceder al dashboard de estadísticas desde el admin.
    Hereda de SurveySubmission pero no crea una tabla nueva.

    Permisos:
    - can_view_statistical_dashboard: Permite acceder al dashboard de estadísticas
    """
    class Meta:
        proxy = True
        verbose_name = "Resumen de Estadísticas"
        verbose_name_plural = "Resumen de Estadísticas"
        # Desactivar permisos por defecto para evitar conflictos con el modelo base
        default_permissions = ()  # No crear permisos add, change, delete, view
        # Definir permisos personalizados para control de acceso
        permissions = [
            ("can_view_statistical_dashboard", "Puede ver el dashboard de estadísticas"),
        ]