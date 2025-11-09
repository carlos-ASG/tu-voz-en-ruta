from apps.transport.models import Unit


class QrGenerator(Unit):
    """
    Modelo proxy para acceder al dashboard de estadísticas desde el admin.
    Hereda de SurveySubmission pero no crea una tabla nueva.
    """
    class Meta:
        proxy = True
        verbose_name = "Generador de QR"
        verbose_name_plural = "Generador de QR"
        # Desactivar permisos por defecto para evitar conflictos con el modelo base
        default_permissions = ()  # No crear permisos add, change, delete, view