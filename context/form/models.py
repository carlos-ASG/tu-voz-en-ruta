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


class ComplaintReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True, verbose_name='Código')
    label = models.CharField(max_length=255, verbose_name='Etiqueta')
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')

    def __str__(self):
        return self.label

    class Meta:
        db_table = 'complaint_reasons'
        verbose_name = 'Motivo de queja'
        verbose_name_plural = 'Motivos de queja'


class Complaint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey('transport.Unit', null=True, blank=True, on_delete=models.SET_NULL, related_name='complaints', verbose_name='Unidad')
    reason = models.ForeignKey(ComplaintReason, null=True, blank=True, on_delete=models.SET_NULL, related_name='complaints', verbose_name='Motivo')
    text = models.TextField(verbose_name='Texto de la queja')
    submitted_at = models.DateTimeField(default=timezone.now)
    # additional fields present in the DB schema
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')

    def __str__(self):
        return f'Queja {self.id} - {self.unit.unit_number if self.unit else "-"}'

    class Meta:
        db_table = 'complaints'
        verbose_name = 'Queja'
        verbose_name_plural = 'Quejas'

class QuestionOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name='Pregunta')
    text = models.CharField(max_length=255, verbose_name='Texto de la opción')
    position = models.IntegerField(verbose_name='Posición de la opción')
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Fecha de actualización')

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'question_options'
        verbose_name = 'Opción de pregunta'
        verbose_name_plural = 'Opciones de preguntas'

class SuverySubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit = models.ForeignKey('transport.Unit', on_delete=models.CASCADE, related_name='submissions', verbose_name='Unidad')
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Submission {self.id} for Unit {self.unit.unit_number}'

    class Meta:
        db_table = 'survey_submissions'
        verbose_name = 'Envío de encuesta'
        verbose_name_plural = 'Envíos de encuestas'

class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(SuverySubmission, on_delete=models.CASCADE, related_name='answers', verbose_name='Envío de encuesta')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Pregunta')
    text_answer = models.TextField(null=True, blank=True, verbose_name='Respuesta de texto')
    rating_answer = models.IntegerField(null=True, blank=True, verbose_name='Respuesta de calificación')
    selected_options = models.ManyToManyField(QuestionOption, blank=True, related_name='answers', verbose_name='Opciones seleccionadas')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')

    def __str__(self):
        return f'Answer {self.id} for Question {self.question.id}'

    class Meta:
        db_table = 'answers'
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'

