from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from transport.models import Unit
from .models import Question, ComplaintReason, SurveySubmission, Answer, Complaint
from .forms.complaint_form import ComplaintForm
from .forms.select_unit_form import SelectUnitForm
from .forms.survery_form import SurveyForm


def index(request):
    return HttpResponse(f"<h1>{request.tenant}</h1>")


def survey_form(request):
    """
    Vista para mostrar el formulario de encuesta con preguntas dinámicas.
    Maneja tres formularios separados: selección de unidad, preguntas de encuesta y quejas.
    """
    unit_id = request.GET.get('unit_id', None)
    
    # Inicializar los tres formularios
    unit_form = SelectUnitForm(unit_id=unit_id, data=request.POST or None)
    survey_form_obj = SurveyForm(data=request.POST or None)
    complaint_form = ComplaintForm(data=request.POST or None)
    
    context = {
        'unit_id': unit_id,
        'unit_form': unit_form,
        'survey_form': survey_form_obj,
        'complaint_form': complaint_form,
    }
    
    return render(request, 'interview/form_section.html', context)


def submit_survey(request):
    """
    Vista para procesar el envío de la encuesta.
    Valida y procesa los tres formularios: unidad, encuesta y quejas.
    El aislamiento por organización es automático gracias al schema del tenant (django-tenants).
    """
    if request.method != 'POST':
        return redirect('interview:survey_form')
    
    # Obtener unit_id desde POST o GET
    unit_id = request.POST.get('unit') or request.GET.get('unit_id')
    
    if not unit_id:
        messages.error(request, 'Debes seleccionar una unidad para continuar.')
        return redirect('interview:survey_form')
    
    # Validar que la unidad pertenece a la organización actual
    unit = get_object_or_404(Unit, id=unit_id)
    
    # Inicializar los tres formularios con los datos POST
    unit_form = SelectUnitForm(unit_id=unit_id, data=request.POST)
    survey_form = SurveyForm(data=request.POST)
    complaint_form = ComplaintForm(data=request.POST)
    
    # Validar todos los formularios
    unit_valid = unit_form.is_valid()
    survey_valid = survey_form.is_valid()
    complaint_valid = complaint_form.is_valid()
    
    if not (unit_valid and survey_valid and complaint_valid):
        # Si algún formulario no es válido, mostrar errores
        messages.error(request, 'Por favor corrige los errores en el formulario.')
        
        context = {
            'unit_id': unit_id,
            'unit_form': unit_form,
            'survey_form': survey_form,
            'complaint_form': complaint_form,
        }
        return render(request, 'interview/form_section.html', context)
    
    # ============================================
    # TODOS LOS FORMULARIOS SON VÁLIDOS
    # ============================================
    
    try:
        # 1. Crear el registro de envío de encuesta
        submission = SurveySubmission.objects.create(
            unit=unit
        )
        
        # 2. Procesar las respuestas a las preguntas del SurveyForm
        for field_name, field_obj in survey_form.fields.items():
            if not field_name.startswith('question_'):
                continue
            
            # Obtener el objeto Question asociado
            question = getattr(field_obj, 'question_obj', None)
            if not question:
                continue
            
            field_value = survey_form.cleaned_data.get(field_name)
            
            if question.type == Question.QuestionType.RATING:
                # Rating: valor entero del 1 al 5
                if field_value:
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        rating_answer=field_value
                    )
            
            elif question.type == Question.QuestionType.TEXT:
                # Texto libre
                if field_value and field_value.strip():
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        text_answer=field_value.strip()
                    )
            
            elif question.type == Question.QuestionType.CHOICE:
                # Opción única (ModelChoiceField devuelve un QuestionOption)
                if field_value:
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        selected_option=field_value
                    )
            
            elif question.type == Question.QuestionType.MULTI_CHOICE:
                # Múltiples opciones (ModelMultipleChoiceField devuelve QuerySet)
                if field_value:
                    answer = Answer.objects.create(
                        submission=submission,
                        question=question
                    )
                    answer.selected_options.set(field_value)
        
        # 3. Procesar la queja del ComplaintForm (si existe)
        complaint_reason = complaint_form.cleaned_data.get('complaint_reason')
        complaint_text = complaint_form.cleaned_data.get('complaint_text', '').strip()
        
        # Crear queja si hay un motivo seleccionado (el texto es opcional)
        has_complaint = False
        if complaint_reason:
            Complaint.objects.create(
                unit=unit,
                reason=complaint_reason,
                text=complaint_text  # Puede ser vacío
            )
            has_complaint = True
        
        messages.success(request, '¡Gracias! Tu encuesta ha sido enviada correctamente.')
        
        # Guardar información en la sesión para la vista de agradecimiento
        request.session['has_complaint'] = has_complaint
        request.session['submission_success'] = True
        
        # Redirigir a la vista de agradecimiento
        return redirect('interview:thank_you')
        
    except Exception as e:
        messages.error(request, f'Ocurrió un error al procesar la encuesta: {str(e)}')
        print(f'Error en submit_survey: {e}')
        
        context = {
            'unit_id': unit_id,
            'unit_form': unit_form,
            'survey_form': survey_form,
            'complaint_form': complaint_form,
        }
        return render(request, 'interview/form_section.html', context)


def thank_you(request):
    """
    Vista de agradecimiento mostrada después de enviar la encuesta.
    """
    # Verificar que el usuario acaba de enviar una encuesta
    submission_success = request.session.get('submission_success', False)
    has_complaint = request.session.get('has_complaint', False)
    
    # Obtener estadísticas del día ANTES de limpiar la sesión
    from django.utils import timezone
    import pytz
    
    # Obtener la zona horaria configurada en settings
    tz = pytz.timezone('America/Mazatlan')
    now = timezone.now().astimezone(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Contar envíos de hoy (el aislamiento por tenant es automático vía schema)
    total_submissions = SurveySubmission.objects.filter(
        submitted_at__gte=today_start
    ).count()
    
    # Preparar contexto ANTES de limpiar sesión
    context = {
        'has_complaint': has_complaint,
        'show_stats': submission_success,
        'total_submissions': total_submissions,
    }
    
    # Limpiar la sesión DESPUÉS de preparar el contexto
    if 'submission_success' in request.session:
        del request.session['submission_success']
    if 'has_complaint' in request.session:
        del request.session['has_complaint']
    
    return render(request, 'interview/thank_view.html', context)
