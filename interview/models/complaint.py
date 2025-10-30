from django.db import models
import uuid
from django.utils import timezone


class Complaint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey('transport.Unit', null=True, blank=True, on_delete=models.SET_NULL, related_name='complaints', verbose_name='Unidad')
    reason = models.ForeignKey('interview.ComplaintReason', null=True, blank=True, on_delete=models.SET_NULL, related_name='complaints', verbose_name='Motivo')
    text = models.TextField(verbose_name='Texto de la queja')
    submitted_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')

    def __str__(self):
        return f'Queja {self.id} - {self.unit.unit_number if self.unit else "-"}'

    class Meta:
        db_table = 'complaints'
        verbose_name = 'Queja'
        verbose_name_plural = 'Quejas'
