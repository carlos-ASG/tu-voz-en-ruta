from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json

from interview.models.survey_submission import SurveySubmission
from interview.models.complaint import Complaint
from interview.models.answer import Answer
from interview.models.question import Question

@login_required
@staff_member_required
def statistics_dashboard(request):
    """
    Vista de dashboard de estadísticas personalizada.
    
    Filtros aplicados:
    1. Organización del usuario autenticado (CRÍTICO)
    2. Período de fechas (hoy, semana, mes, año, todo)
    """
    
    # FILTRO CRÍTICO: Obtener organización del usuario
    user_organization = request.user.organization
    
    if not user_organization:
        # Si el usuario no tiene organización asignada, mostrar página vacía
        context = {
            'error_message': 'Tu usuario no tiene una organización asignada. Contacta al administrador.',
            'has_data': False,
        }
        return render(request, 'statistical_summary/statistics_dashboard.html', context)
    
    # Obtener período de filtro desde parámetros GET
    period = request.GET.get('period', 'all')
    
    # Calcular rango de fechas según el período seleccionado
    now = timezone.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = 'Hoy'
    elif period == 'week':
        start_date = now - timedelta(days=now.weekday())  # Lunes de esta semana
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = 'Esta Semana'
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = 'Este Mes'
    elif period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = 'Este Año'
    else:  # 'all'
        start_date = None
        period_label = 'Todo el Tiempo'
    
    # Base queryset filters (organización + fecha)
    base_filters = {'organization': user_organization}
    if start_date:
        date_filter = Q(submitted_at__gte=start_date)
    else:
        date_filter = Q()
    
    # ==================== KPI 1: Total de Envíos de Encuestas ====================
    submissions_qs = SurveySubmission.objects.filter(**base_filters)
    if start_date:
        submissions_qs = submissions_qs.filter(submitted_at__gte=start_date)
    total_submissions = submissions_qs.count()
    
    # ==================== KPI 2: Total de Quejas ====================
    complaints_qs = Complaint.objects.filter(**base_filters)
    if start_date:
        complaints_qs = complaints_qs.filter(submitted_at__gte=start_date)
    total_complaints = complaints_qs.count()
    
    # ==================== KPI 3: Calificación Promedio ====================
    answers_qs = Answer.objects.filter(organization=user_organization, rating_answer__isnull=False)
    if start_date:
        # Filtrar por fecha del submission relacionado
        answers_qs = answers_qs.filter(submission__submitted_at__gte=start_date)
    
    avg_rating_result = answers_qs.aggregate(avg_rating=Avg('rating_answer'))
    avg_rating = round(avg_rating_result['avg_rating'], 2) if avg_rating_result['avg_rating'] else 0
    
    # ==================== GRÁFICO 1: Top 5 Motivos de Queja ====================
    top_reasons = (
        complaints_qs
        .values('reason__label')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    
    chart1_labels = [item['reason__label'] or 'Sin motivo' for item in top_reasons]
    chart1_data = [item['count'] for item in top_reasons]
    
    # ==================== GRÁFICO 2: Top 5 Unidades con más Quejas ====================
    top_units = (
        complaints_qs
        .values('unit__unit_number')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    
    chart2_labels = [f"Unidad {item['unit__unit_number']}" if item['unit__unit_number'] else 'Sin unidad' for item in top_units]
    chart2_data = [item['count'] for item in top_units]
    
    # ==================== GRÁFICO 3: Envíos por Día (Línea de Tiempo) ====================
    # Agrupar submissions por día dentro del período
    if period == 'today':
        # Para hoy, agrupar por hora
        submissions_timeline = (
            submissions_qs
            .extra(select={'hour': "EXTRACT(hour FROM submitted_at)"})
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour')
        )
        chart3_labels = [f"{int(item['hour'])}:00" for item in submissions_timeline]
        chart3_data = [item['count'] for item in submissions_timeline]
    else:
        # Para otros períodos, agrupar por día
        submissions_timeline = (
            submissions_qs
            .extra(select={'date': "DATE(submitted_at)"})
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        chart3_labels = [str(item['date']) for item in submissions_timeline]
        chart3_data = [item['count'] for item in submissions_timeline]
    
    # ==================== GRÁFICO 4: Calificación Promedio por Pregunta (Radar/Barras) ====================
    rating_questions = Question.objects.filter(
        Organization=user_organization,
        type=Question.QuestionType.RATING,
        active=True
    )
    
    rating_by_question = []
    for question in rating_questions:
        answers_for_q = answers_qs.filter(question=question)
        avg_for_q = answers_for_q.aggregate(avg=Avg('rating_answer'))['avg']
        if avg_for_q is not None:
            rating_by_question.append({
                'question': question.text[:30] + '...' if len(question.text) > 30 else question.text,
                'avg': round(avg_for_q, 2)
            })
    
    chart4_labels = [item['question'] for item in rating_by_question]
    chart4_data = [item['avg'] for item in rating_by_question]
    
    # ==================== GRÁFICO 5: Distribución de Respuestas para Pregunta CHOICE (Pie) ====================
    # Seleccionar la primera pregunta activa de tipo CHOICE para el ejemplo
    choice_question = Question.objects.filter(
        Organization=user_organization,
        type=Question.QuestionType.CHOICE,
        active=True
    ).first()
    
    chart5_labels = []
    chart5_data = []
    chart5_question_text = ''
    
    if choice_question:
        chart5_question_text = choice_question.text
        # Obtener distribución de selected_option para esta pregunta
        answers_choice = Answer.objects.filter(
            organization=user_organization,
            question=choice_question,
            selected_option__isnull=False
        )
        
        if start_date:
            answers_choice = answers_choice.filter(submission__submitted_at__gte=start_date)
        
        distribution = (
            answers_choice
            .values('selected_option__text')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        chart5_labels = [item['selected_option__text'] for item in distribution]
        chart5_data = [item['count'] for item in distribution]
    
    # ==================== Preparar Contexto para el Template ====================
    context = {
        'has_data': True,
        'period': period,
        'period_label': period_label,
        'organization_name': user_organization.name,
        
        # KPIs
        'total_submissions': total_submissions,
        'total_complaints': total_complaints,
        'avg_rating': avg_rating,
        
        # Datos para gráficos (convertidos a JSON para JavaScript)
        'chart1_labels': json.dumps(chart1_labels),
        'chart1_data': json.dumps(chart1_data),
        
        'chart2_labels': json.dumps(chart2_labels),
        'chart2_data': json.dumps(chart2_data),
        
        'chart3_labels': json.dumps(chart3_labels),
        'chart3_data': json.dumps(chart3_data),
        
        'chart4_labels': json.dumps(chart4_labels),
        'chart4_data': json.dumps(chart4_data),
        
        'chart5_labels': json.dumps(chart5_labels),
        'chart5_data': json.dumps(chart5_data),
        'chart5_question_text': chart5_question_text,
    }
    
    return render(request, 'statistical_summary/statistics_dashboard.html', context)
