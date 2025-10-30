from django.db import models
import uuid
from django.utils import timezone


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(verbose_name='Texto de la pregunta')

    class QuestionType(models.TextChoices):
        RATING = 'rating', 'Calificación'
        TEXT = 'text', 'Texto'
        CHOICE = 'choice', 'Opción'
        MULTI_CHOICE = 'multi_choice', 'Múltiples opciones'

    type = models.CharField(
        max_length=16,
        choices=QuestionType.choices,
        verbose_name='Tipo de pregunta',
        default=QuestionType.RATING,
    )
    position = models.IntegerField(verbose_name='Posición de la pregunta')
    active = models.BooleanField(default=True, verbose_name='¿Activa?')
    # timestamps managed by DB triggers; show but do not allow editing in admin
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')
    
    def __str__(self):
        return str(self.text[:50])
    
    class Meta:
        db_table = 'questions'
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
