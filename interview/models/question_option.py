from django.db import models
import uuid
from django.utils import timezone


class QuestionOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # refer to Question by string to avoid import cycles
    question = models.ForeignKey('interview.Question', on_delete=models.CASCADE, related_name='options', verbose_name='Pregunta')
    text = models.CharField(max_length=255, verbose_name='Texto de la opción')
    position = models.IntegerField(verbose_name='Posición de la opción')
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')
    organization = models.ForeignKey(
        'organization.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='question_options',
        verbose_name='Organización'
    )

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'question_options'
        verbose_name = 'Opción de pregunta'
        verbose_name_plural = 'Opciones de preguntas'
