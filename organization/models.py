import uuid
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Organization(TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
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
    pass
