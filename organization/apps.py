from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'organization'
    verbose_name = 'Organización'
    verbose_name_plural = 'Organizaciones'


    # def ready(self):
    #     # importar señales para que se registren al arrancar Django
    #     try:
    #         import organization.signals  # noqa: F401
    #     except Exception:
    #         # no fallar el arranque si algo va mal en import (loguear si lo deseas)
    #         pass
