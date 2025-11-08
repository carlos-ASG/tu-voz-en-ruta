import uuid
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Organization(TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
        help_text='Indica si la organización está activa y puede recibir solicitudes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Configuración para crear el esquema automáticamente
    auto_create_schema = True
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organización'
        verbose_name_plural = 'Organizaciones'

class Domain(DomainMixin):
    class Meta:
        verbose_name = 'Dominio'
        verbose_name_plural = 'Dominios'
