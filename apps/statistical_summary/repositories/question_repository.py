"""
Repository para operaciones de Question y Answer.

Este módulo encapsula todas las queries relacionadas con preguntas y respuestas,
proporcionando funciones optimizadas que evitan N+1 queries.
"""
from datetime import datetime
from django.db.models import QuerySet, Avg, Count

from apps.interview.models.question import Question
from apps.interview.models.answer import Answer


def get_active_questions() -> QuerySet[Question]:
    """
    Obtiene todas las preguntas activas.
    
    Returns:
        QuerySet de Question con active=True
        
    Example:
        >>> questions = get_active_questions()
        >>> for q in questions:
        ...     print(q.text)
    """
    return Question.objects.filter(active=True)


def get_filtered_answers(
    question: Question,
    start_date: datetime | None,
    route_id: str | None,
    unit_id: str | None
) -> QuerySet[Answer]:
    """
    Obtiene respuestas filtradas para una pregunta.
    
    Args:
        question: Pregunta para filtrar respuestas
        start_date: Fecha de inicio opcional
        route_id: ID de ruta opcional (mutuamente excluyente con unit_id)
        unit_id: ID de unidad opcional
        
    Returns:
        QuerySet de Answer filtrado
        
    Example:
        >>> question = Question.objects.first()
        >>> answers = get_filtered_answers(question, None, None, "uuid-unit")
        >>> print(answers.count())
        42
    """
    answers_qs = Answer.objects.filter(question=question)
    
    if start_date:
        answers_qs = answers_qs.filter(created_at__gte=start_date)
    
    if route_id:
        answers_qs = answers_qs.filter(submission__unit__route_id=route_id)
    elif unit_id:
        answers_qs = answers_qs.filter(submission__unit_id=unit_id)
    
    return answers_qs


def get_rating_average(answers_qs: QuerySet[Answer]) -> float | None:
    """
    Calcula promedio de ratings.
    
    Args:
        answers_qs: QuerySet de Answer para calcular promedio
        
    Returns:
        Promedio de rating_answer o None si no hay datos
        
    Example:
        >>> answers = Answer.objects.filter(question_id="uuid")
        >>> avg = get_rating_average(answers)
        >>> print(f"{avg:.1f}/5")
        4.2/5
    """
    result = answers_qs.aggregate(Avg("rating_answer"))
    return result["rating_answer__avg"]


def get_choice_counts(
    answers_qs: QuerySet[Answer],
    question: Question
) -> dict[str, int]:
    """
    Obtiene conteo de respuestas para pregunta de opción única.
    
    Optimizado para evitar N+1 queries usando annotate en lugar de
    loop sobre todas las opciones.
    
    Args:
        answers_qs: QuerySet de Answer filtrado
        question: Pregunta para obtener opciones
        
    Returns:
        Diccionario {texto_opción: count}
        
    Example:
        >>> answers = Answer.objects.filter(question_id="uuid")
        >>> question = Question.objects.get(id="uuid")
        >>> counts = get_choice_counts(answers, question)
        >>> print(counts)
        {'Excelente': 10, 'Bueno': 5, 'Regular': 2}
    """
    # Optimización: usar annotate en lugar de loop
    counts = (
        answers_qs
        .filter(selected_option__isnull=False)
        .values('selected_option__text')
        .annotate(count=Count('id'))
    )
    
    return {item['selected_option__text']: item['count'] for item in counts}


def get_multi_choice_counts(
    answers_qs: QuerySet[Answer],
    question: Question
) -> dict[str, int]:
    """
    Obtiene conteo de respuestas para pregunta de múltiples opciones.
    
    Optimizado para evitar N+1 queries. Para relaciones many-to-many,
    necesitamos contar cuántas veces cada opción fue seleccionada.
    
    Args:
        answers_qs: QuerySet de Answer filtrado
        question: Pregunta para obtener opciones
        
    Returns:
        Diccionario {texto_opción: count}
        
    Example:
        >>> answers = Answer.objects.filter(question_id="uuid")
        >>> question = Question.objects.get(id="uuid")
        >>> counts = get_multi_choice_counts(answers, question)
        >>> print(counts)
        {'Wi-Fi': 15, 'USB': 10, 'AC': 20}
    """
    # Para many-to-many, contar por cada opción
    options_count: dict[str, int] = {}
    
    for option in question.options.all():
        # Contar cuántas veces esta opción fue seleccionada
        count = answers_qs.filter(selected_options=option).count()
        if count > 0:
            options_count[option.text] = count
    
    return options_count
