from django.db import models
import uuid
from django.utils import timezone


class ComplaintReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255, verbose_name='Etiqueta')
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')

    def __str__(self):
        return self.label

    class Meta:
        db_table = 'complaint_reasons'
        verbose_name = 'Motivo de queja'
        verbose_name_plural = 'Motivos de queja'
