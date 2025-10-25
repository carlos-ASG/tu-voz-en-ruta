from django.db import models
import uuid
from django.utils import timezone


class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey('interview.SurveySubmission', on_delete=models.CASCADE, related_name='answers', verbose_name='Envío de encuesta')
    question = models.ForeignKey('interview.Question', on_delete=models.CASCADE, related_name='answers', verbose_name='Pregunta')
    
    # Para QuestionType.TEXT
    text_answer = models.TextField(null=True, blank=True, verbose_name='Respuesta de texto')
    
    # Para QuestionType.RATING
    rating_answer = models.IntegerField(null=True, blank=True, verbose_name='Respuesta de calificación')
    
    # Para QuestionType.CHOICE (Opción única)
    selected_option = models.ForeignKey(
        'interview.QuestionOption',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='single_answers',
        verbose_name='Opción seleccionada'
    )
    
    # Para QuestionType.MULTI_CHOICE (Opciones múltiples)
    selected_options = models.ManyToManyField(
        'interview.QuestionOption',
        blank=True,
        related_name='multi_answers',
        verbose_name='Opciones seleccionadas'
    )
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    
    organization = models.ForeignKey(
        'organization.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='answers',
        verbose_name='Organización'
    )

    def __str__(self):
        return f'Answer {self.id} for Question {self.question.id}'

    class Meta:
        db_table = 'answers'
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
