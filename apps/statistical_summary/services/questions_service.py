"""
Service para lógica de negocio de preguntas.

Este módulo contiene la lógica de negocio para calcular estadísticas
de preguntas activas según su tipo (rating, choice, multi_choice).
"""
from datetime import datetime

from apps.interview.models.question import Question
from ..repositories import question_repository
from ..schemas import QuestionStatistic
from ..constants import QUESTION_TYPE_LABELS


def get_questions_statistics(
    start_date: datetime | None,
    route_id: str | None = None,
    unit_id: str | None = None
) -> dict[str, QuestionStatistic]:
    """
    Calcula estadísticas de todas las preguntas activas.
    
    El aislamiento por organización es automático vía schema del tenant.
    
    Args:
        start_date: Fecha de inicio para filtrar respuestas
        route_id: ID de ruta opcional
        unit_id: ID de unidad opcional
        
    Returns:
        Diccionario {texto_pregunta: QuestionStatistic}
        
    Example:
        >>> from datetime import datetime
        >>> stats = get_questions_statistics(datetime.now())
        >>> for text, stat in stats.items():
        ...     print(f"{text}: {stat.type} = {stat.summary}")
        ¿Cómo califica el servicio?: calificación = 4.2/5
        ¿El conductor fue amable?: opción = {'Sí': 10, 'No': 2}
    """
    questions = question_repository.get_active_questions()
    statistics: dict[str, QuestionStatistic] = {}
    
    for question in questions:
        answers_qs = question_repository.get_filtered_answers(
            question, start_date, route_id, unit_id
        )
        
        # Procesar según tipo de pregunta usando match/case (Python 3.10+)
        match question.type:
            case Question.QuestionType.RATING:
                stat = _process_rating_question(question, answers_qs)
            case Question.QuestionType.CHOICE:
                stat = _process_choice_question(question, answers_qs)
            case Question.QuestionType.MULTI_CHOICE:
                stat = _process_multi_choice_question(question, answers_qs)
            case _:
                # Ignorar otros tipos (TEXT según especificación)
                continue
        
        statistics[question.text] = stat
    
    return statistics


def _process_rating_question(
    question: Question,
    answers_qs
) -> QuestionStatistic:
    """
    Procesa pregunta tipo RATING.
    
    Args:
        question: Pregunta a procesar
        answers_qs: QuerySet de Answer filtrado
        
    Returns:
        QuestionStatistic con promedio de rating
        
    Example:
        >>> stat = _process_rating_question(question, answers)
        >>> print(stat.summary)
        4.2/5
    """
    avg_rating = question_repository.get_rating_average(answers_qs)
    
    if avg_rating is not None:
        summary = f"{avg_rating:.1f}/5"
    else:
        summary = "Sin datos"
    
    return QuestionStatistic(
        type=QUESTION_TYPE_LABELS["RATING"],
        summary=summary
    )


def _process_choice_question(
    question: Question,
    answers_qs
) -> QuestionStatistic:
    """
    Procesa pregunta tipo CHOICE (opción única).
    
    Args:
        question: Pregunta a procesar
        answers_qs: QuerySet de Answer filtrado
        
    Returns:
        QuestionStatistic con conteo por opción
        
    Example:
        >>> stat = _process_choice_question(question, answers)
        >>> print(stat.summary)
        {'Excelente': 10, 'Bueno': 5, 'Regular': 2}
    """
    options_count = question_repository.get_choice_counts(answers_qs, question)
    
    return QuestionStatistic(
        type=QUESTION_TYPE_LABELS["CHOICE"],
        summary=options_count if options_count else "Sin datos"
    )


def _process_multi_choice_question(
    question: Question,
    answers_qs
) -> QuestionStatistic:
    """
    Procesa pregunta tipo MULTI_CHOICE (múltiples opciones).
    
    Args:
        question: Pregunta a procesar
        answers_qs: QuerySet de Answer filtrado
        
    Returns:
        QuestionStatistic con conteo por opción
        
    Example:
        >>> stat = _process_multi_choice_question(question, answers)
        >>> print(stat.summary)
        {'Wi-Fi': 15, 'USB': 10, 'AC': 20}
    """
    options_count = question_repository.get_multi_choice_counts(answers_qs, question)
    
    return QuestionStatistic(
        type=QUESTION_TYPE_LABELS["MULTI_CHOICE"],
        summary=options_count if options_count else "Sin datos"
    )
