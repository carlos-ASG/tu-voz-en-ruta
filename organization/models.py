import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organización'
        verbose_name_plural = 'Organizaciones'

class User(AbstractUser):
    organization = models.ForeignKey(
        Organization, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='users'
    )
    
    is_president = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Nombre de ruta')
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='routes',
        verbose_name='Organización'
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'routes'
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit_number = models.CharField(max_length=4, unique=True, verbose_name='Número de unidad')
    route = models.ForeignKey(Route, null=True, blank=True, on_delete=models.SET_NULL, related_name='units', verbose_name='Ruta')
    metadata = models.JSONField(null=True, blank=True)
    # timestamps: managed by DB defaults and triggers; not editable via admin
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')

    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='units',
        verbose_name='Organización'
    )

    def __str__(self):
        return str(self.unit_number)

    class Meta:
        db_table = 'units'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

