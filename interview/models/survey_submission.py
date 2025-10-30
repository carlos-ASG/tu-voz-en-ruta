from django.db import models
import uuid
from django.utils import timezone


class SurveySubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey('transport.Unit', on_delete=models.CASCADE, related_name='submissions', verbose_name='Unidad')
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Submission {self.id} for Unit {self.unit.unit_number}'

    class Meta:
        db_table = 'survey_submissions'
        verbose_name = 'Envío de encuesta'
        verbose_name_plural = 'Envíos de encuestas'
