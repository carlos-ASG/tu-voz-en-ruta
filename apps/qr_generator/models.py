from apps.transport.models import Unit


class QrGenerator(Unit):
    """
    Modelo proxy para acceder al generador de códigos QR desde el admin.
    Hereda de Unit pero no crea una tabla nueva.

    Permisos:
    - can_generate_qr_codes: Permite generar códigos QR para unidades
    """
    class Meta:
        proxy = True
        verbose_name = "Generador de QR"
        verbose_name_plural = "Generador de QR"
        # Desactivar permisos por defecto para evitar conflictos con el modelo base
        default_permissions = ()  # No crear permisos add, change, delete, view
        # Definir permisos personalizados para control de acceso
        permissions = [
            ("can_generate_qr_codes", "Puede generar códigos QR para unidades"),
        ]