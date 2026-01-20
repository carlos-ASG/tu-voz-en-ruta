from tracemalloc import start
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Avg, Count, Q
import json

from apps.interview.models.complaint import Complaint
from apps.interview.models.survey_submission import SurveySubmission
from apps.interview.models.question import Question
from apps.interview.models.answer import Answer
from apps.interview.models.question_option import QuestionOption
from apps.transport.models import Route, Unit
import pytz


def calculate_statistics(period: str, route_id: str = None, unit_id: str = None) -> dict:
    """
    Calcula estadísticas filtradas por período, ruta o unidad.
    El aislamiento por organización es automático via schema del tenant.
    """
    start_date, period_label = get_start_date(period)

    # Base queryset filters (sin organization, el schema ya filtra)
    submissions_filters = {}
    complaints_filters = {}
    
    # Agregar filtro de fecha si existe
    if start_date:
        submissions_filters['submitted_at__gte'] = start_date
        complaints_filters['submitted_at__gte'] = start_date
    
    # Agregar filtro por ruta o unidad (son mutuamente excluyentes)
    if route_id:
        submissions_filters['unit__route_id'] = route_id
        complaints_filters['unit__route_id'] = route_id
    elif unit_id:
        submissions_filters['unit_id'] = unit_id
        complaints_filters['unit_id'] = unit_id
    
    # ==================== KPI 1: Total de Envíos de Encuestas ====================
    total_submissions = SurveySubmission.objects.filter(**submissions_filters).count()
    
    # ==================== KPI 2: Total de Quejas ====================
    # ✅ Renombrar la llamada para evitar conflicto de nombres
    complaints_data = get_complaints_summary(complaints_filters)
    total_complaints = complaints_data.get('total_complaints', 0)
    complaints_by_reason = complaints_data.get('by_reason', {})
    
    # Obtener resumen de quejas por unidad (número de tránsito)
    complaints_by_unit = get_complaints_by_unit(complaints_filters)

    # ==================== KPI 3: Resumen de Preguntas ====================
    questions_statistics = questions_summary(start_date, route_id, unit_id)

    # ==================== KPI 4: Línea de tiempo de envíos ====================
    # Si el período es "today", agrupar por hora en lugar de por día
    group_by_hour = (period == "today")
    survey_timeline = get_survey_submissions_timeline(submissions_filters, group_by_hour=group_by_hour)
    
    return {
        "period_label": period_label,
        "total_submissions": total_submissions,
        "total_complaints": total_complaints,
        "complaints_by_reason": complaints_by_reason,
        "complaints_by_unit": complaints_by_unit,
        "questions_statistics": questions_statistics,
        "survey_submissions_timeline": survey_timeline,
    }

def get_survey_submissions_timeline(submissions_filters: dict, group_by_hour: bool = False) -> dict:
    """Retorna una línea de tiempo de envíos de encuestas.

    Args:
        submissions_filters: filtros a aplicar sobre SurveySubmission queryset (ej. fecha, unit_id)
        group_by_hour: si es True, agrupa por hora; si es False, agrupa por día

    Returns:
        dict: {
            'dates': [str, ...],  # Fechas en formato 'YYYY-MM-DD' o 'MM-DD HH:00'
            'counts': [int, ...]  # Conteo de envíos por fecha/hora
        }
    """
    from django.db.models.functions import TruncDate, TruncHour
    
    if group_by_hour:
        # Agrupar por hora
        submissions_by_time = (
            SurveySubmission.objects.filter(**submissions_filters)
            .annotate(time=TruncHour('submitted_at'))
            .values('time')
            .annotate(count=Count('id'))
            .order_by('time')
        )
    else:
        # Agrupar por día
        submissions_by_time = (
            SurveySubmission.objects.filter(**submissions_filters)
            .annotate(time=TruncDate('submitted_at'))
            .values('time')
            .annotate(count=Count('id'))
            .order_by('time')
        )
    
    # Separar en listas de fechas y conteos
    dates = []
    counts = []
    
    for item in submissions_by_time:
        time_obj = item.get('time')
        if time_obj:
            if group_by_hour:
                # Formato: 'HH:00'
                dates.append(time_obj.strftime('%H:00'))
            else:
                # Formato: 'YYYY-MM-DD'
                dates.append(time_obj.strftime('%Y-%m-%d'))
            counts.append(item.get('count', 0))
    
    return {
        'dates': dates,
        'counts': counts,
    }


def get_complaints_summary(complaints_filters: dict) -> dict:
    """Retorna un resumen de quejas.

    Args:
        complaints_filters: filtros a aplicar sobre Complaint queryset (ej. fecha, unit_id)

    Returns:
        dict: {
            'total_complaints': int,
            'by_reason': {
                'motivo': count,
                ...
            }
        }
    """
    qs = Complaint.objects.filter(**complaints_filters)
    total_complaints = qs.count()

    # Agrupar por motivo de la queja y contar
    reason_counts = (
        qs.values('reason__label')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Convertir a diccionario simple: {motivo: count}
    by_reason = {}
    for item in reason_counts:
        label = item.get('reason__label') or 'Sin motivo'
        count = item.get('count', 0)
        by_reason[label] = count

    return {
        'total_complaints': total_complaints,
        'by_reason': by_reason,
    }


def get_complaints_by_unit(complaints_filters: dict) -> dict:
    """Retorna un resumen de quejas agrupadas por número de tránsito de unidad.

    Args:
        complaints_filters: filtros a aplicar sobre Complaint queryset (ej. fecha, unit_id)

    Returns:
        dict: {
            'transit_number': count,
            ...
        }
        Ejemplo: {
            'ABC123': 5,
            'XYZ789': 3,
            'DEF456': 1
        }
    """
    # Filtrar quejas y agrupar por unidad
    complaints_by_unit = (
        Complaint.objects.filter(**complaints_filters)
        .exclude(unit__isnull=True)  # Excluir quejas sin unidad asociada
        .values('unit__transit_number')
        .annotate(count=Count('id'))
        .order_by('-count')  # Ordenar por cantidad de quejas (descendente)
    )

    # Convertir a diccionario simple: {transit_number: count}
    by_unit = {}
    for item in complaints_by_unit:
        transit_number = item.get('unit__transit_number')
        count = item.get('count', 0)
        if transit_number:
            by_unit[transit_number] = count

    return by_unit
    

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


def questions_summary(start_date: datetime, route_id: str = None, unit_id: str = None) -> dict:
    """
    Recolecta estadísticas de preguntas activas según su tipo.
    El aislamiento por organización es automático via schema del tenant.

    Returns:
        dict: {
            "Texto de la pregunta": {
                "type": "rating" | "choice" | "multi_choice",
                "summary": <valor_según_tipo>
            }
        }
    """

    # Obtener todas las preguntas activas (el schema ya filtra por tenant)
    questions = Question.objects.filter(active=True)

    statistics = {}

    for question in questions:
        # Filtrar respuestas por pregunta (sin organization, el schema filtra)
        answers_qs = Answer.objects.filter(question=question)
        
        # Filtrar por fecha si existe
        if start_date:
            answers_qs = answers_qs.filter(created_at__gte=start_date)
        
        # Filtrar por ruta o unidad si existen
        if route_id:
            answers_qs = answers_qs.filter(submission__unit__route_id=route_id)
        elif unit_id:
            answers_qs = answers_qs.filter(submission__unit_id=unit_id)

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


def get_units_and_routes() -> dict:
    """
    Obtiene las rutas y unidades del tenant actual.
    El aislamiento por organización es automático via schema del tenant.
        
    Returns:
        dict: {
            "routes": [{"id": uuid, "name": str}, ...],
            "units": [{"id": uuid, "transit_number": str}, ...]  # ✅ Cambiar 'unit_number' a 'transit_number'
        }
    """
    # Obtener rutas (el schema ya filtra por tenant)
    routes = Route.objects.order_by('name').values('id', 'name')
    
    # ✅ Cambiar 'unit_number' por 'transit_number'
    units = Unit.objects.order_by('transit_number').values('id', 'transit_number')
    
    return {
        "routes": list(routes),
        "units": list(units),
    }
