from tracemalloc import start
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Avg, Count, Q
import json

from interview.models.complaint import Complaint
from interview.models.survey_submission import SurveySubmission
from interview.models.question import Question
from interview.models.answer import Answer
from interview.models.question_option import QuestionOption
import pytz


def calculate_statistics(period: str, organization: str) -> dict:
    start_date, period_label = get_start_date(period)

    # Si start_date es None (period='all'), no filtrar por fecha
    if start_date:
    # ==================== KPI 1: Total de Envíos de Encuestas ====================
        
        total_submissions = SurveySubmission.objects.filter(
            organization=organization, submitted_at__gte=start_date
        ).count()
        # ==================== KPI 2: Total de Quejas ====================
        total_complaints = Complaint.objects.filter(
            organization=organization, submitted_at__gte=start_date
        ).count()
    else:
    # ==================== KPI 1: Total de Envíos de Encuestas ====================
        
        total_submissions = SurveySubmission.objects.filter(
            organization=organization
        ).count()
        
        # ==================== KPI 2: Total de Quejas ====================
        
        total_complaints = Complaint.objects.filter(
            organization=organization
        ).count()
        

    # ==================== KPI 3: Resumen de Preguntas ====================
    questions_statistics = questions_summary(organization, start_date)

    return {
        "period_label": period_label,
        "total_submissions": total_submissions,
        "total_complaints": total_complaints,
        "questions_statistics": questions_statistics,
    }


def get_start_date(period: str) -> tuple[datetime, str]:
    # Calcular rango de fechas según el período seleccionado
    # Obtener hora actual (siempre en UTC si USE_TZ=True)
    now_utc: datetime = timezone.now()  # 2025-10-26 01:02:28+00:00

    # Convertir a zona horaria local configurada
    local_tz = pytz.timezone("America/Mazatlan")
    now_local: datetime = now_utc.astimezone(local_tz)

    if period == "today":
        # Inicio del día en hora local
        start_date = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "Hoy"
    elif period == "week":
        # Lunes de esta semana en hora local
        start_date = now_local - timedelta(days=now_local.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "Esta Semana"
    elif period == "month":
        # Primer día del mes en hora local
        start_date = now_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = "Este Mes"
    elif period == "year":
        # Primer día del año en hora local
        start_date = now_local.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        period_label = "Este Año"
    else:  # 'all'
        start_date = None
        period_label = "Todo el Tiempo"

    return start_date, period_label


def questions_summary(organization: str, start_date: datetime) -> dict:
    """
    Recolecta estadísticas de preguntas activas según su tipo.

    Returns:
        dict: {
            "Texto de la pregunta": {
                "type": "rating" | "choice" | "multi_choice",
                "summary": <valor_según_tipo>
            }
        }
    """

    # Obtener todas las preguntas activas de la organización
    questions = Question.objects.filter(Organization=organization, active=True)

    statistics = {}

    for question in questions:
        # Filtrar respuestas por fecha
        answers_qs = Answer.objects.filter(question=question, organization=organization)
        if start_date:
            answers_qs = answers_qs.filter(created_at__gte=start_date)

        # Procesar según tipo de pregunta
        if question.type == Question.QuestionType.RATING:
            # Calcular promedio de rating
            avg_rating = answers_qs.aggregate(Avg("rating_answer"))[
                "rating_answer__avg"
            ]
            if avg_rating is not None:
                statistics[question.text] = {
                    "type": "calificación",
                    "summary": f"{avg_rating:.1f}/5",
                }
            else:
                statistics[question.text] = {
                    "type": "calificación",
                    "summary": "Sin datos",
                }

        elif question.type == Question.QuestionType.CHOICE:
            # Contar respuestas por opción
            options_count = {}
            for option in question.options.all():
                count = answers_qs.filter(selected_option=option).count()
                if count > 0:
                    options_count[option.text] = count

            statistics[question.text] = {
                "type": "opción",
                # Convertir dict a JSON string para evitar errores de comillas en HTML
                "summary": json.dumps(options_count) if options_count else "Sin datos",
            }

        elif question.type == Question.QuestionType.MULTI_CHOICE:
            # Contar respuestas por opción (many-to-many)
            options_count = {}
            for option in question.options.all():
                # Contar cuántas veces esta opción fue seleccionada
                count = answers_qs.filter(selected_options=option).count()
                if count > 0:
                    options_count[option.text] = count

            statistics[question.text] = {
                "type": "múltiples opciones",
                # Convertir dict a JSON string para evitar errores de comillas en HTML
                "summary": json.dumps(options_count) if options_count else "Sin datos",
            }

        # Ignorar tipo TEXT según especificación

    return statistics
