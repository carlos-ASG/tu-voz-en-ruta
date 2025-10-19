from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TransportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transport'
    verbose_name = _('Transporte')
    verbose_name_plural = _('Transporte')
