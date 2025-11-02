import uuid
from django.db import models
from django.utils import timezone

class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Nombre de ruta')
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'routes'
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transit_number = models.CharField(max_length=25, unique=True, verbose_name='Número de tránsito')
    internal_number = models.CharField(max_length=8, blank=True, verbose_name='Número de interno')
    owner = models.CharField(max_length=255, null=True, blank=True, verbose_name='Propietario')
    route = models.ForeignKey(Route, null=True, blank=True, on_delete=models.SET_NULL, related_name='units', verbose_name='Ruta')
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')

    def __str__(self):
        return str(self.transit_number)

    class Meta:
        db_table = 'units'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
