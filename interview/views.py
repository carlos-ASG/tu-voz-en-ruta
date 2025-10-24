from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from organization.models import Unit, Organization
from .models import Question, ComplaintReason, SurveySubmission, Answer, Complaint
from .forms.survery_form import SurveyForm
from .forms.select_unit_form import SelectUnitForm

def select_unit(request):
    """
    Vista para seleccionar la unidad antes de mostrar el formulario de encuesta.
    Muestra todas las unidades de todas las organizaciones.
    Al enviar, redirige automáticamente al formulario de la organización y unidad seleccionada.
    """
    if request.method == 'POST':
        form = SelectUnitForm(request.POST)
        if form.is_valid():
            unit = form.get_selected_unit()
            # Redirigir al formulario de encuesta con la organización y unidad seleccionadas
            return redirect('interview:survey_form', 
                          organization_id=unit.organization.id, 
                          unit_id=unit.id)
        else:
            # Si el formulario no es válido, volver a mostrar con errores
            context = {'form': form}
            return render(request, 'interview/select_unit.html', context)
    else:
        # GET: mostrar formulario vacío
        form = SelectUnitForm()
        context = {'form': form}
        return render(request, 'interview/select_unit.html', context)


def survey_form(request, organization_id, unit_id):
    """
    Vista para mostrar el formulario de encuesta con preguntas dinámicas.
    """
    organization = get_object_or_404(Organization, id=organization_id)
    unit = get_object_or_404(Unit, id=unit_id, organization_id=organization_id)
    
    # Crear el formulario con las preguntas de la organización
    form = SurveyForm(organization_id=organization_id)
    
    # Obtener preguntas para renderizar (con sus opciones)
    questions = Question.objects.filter(
        active=True,
        Organization_id=organization_id
    ).prefetch_related('options').order_by('position')
    
    context = {
        'organization': organization,
        'organization_id': organization_id,
        'unit': unit,
        'unit_id': unit_id,
        'form': form,
        'questions': questions,
        'complaint_reasons': ComplaintReason.objects.filter(
            organization_id=organization_id
        ).order_by('label'),
    }
    return render(request, 'interview/form_section.html', context)


def submit_survey(request, organization_id, unit_id):
    """
    Vista para procesar el envío de la encuesta.
    """
    if request.method != 'POST':
        return redirect('interview:survey_form', organization_id=organization_id, unit_id=unit_id)
    
    organization = get_object_or_404(Organization, id=organization_id)
    unit = get_object_or_404(Unit, id=unit_id, organization_id=organization_id)
    
    # Crear el formulario con los datos POST
    form = SurveyForm(organization_id=organization_id, data=request.POST)
    
    if form.is_valid():
        try:
            # 1. Crear el registro de envío de encuesta con organización
            submission = SurveySubmission.objects.create(
                unit=unit,
                organization=organization
            )
            
            # 2. Procesar las respuestas a las preguntas
            questions = Question.objects.filter(
                active=True,
                Organization_id=organization_id
            )
            
            for question in questions:
                field_name = f'question_{question.id}'
                
                if field_name not in form.cleaned_data:
                    continue
                
                field_value = form.cleaned_data[field_name]
                
                if question.type == Question.QuestionType.RATING:
                    # Rating: valor entero del 1 al 5
                    if field_value:
                        Answer.objects.create(
                            submission=submission,
                            question=question,
                            rating_answer=field_value,
                            organization=organization
                        )
                
                elif question.type == Question.QuestionType.TEXT:
                    # Texto libre
                    if field_value and field_value.strip():
                        Answer.objects.create(
                            submission=submission,
                            question=question,
                            text_answer=field_value.strip(),
                            organization=organization
                        )
                
                elif question.type == Question.QuestionType.CHOICE:
                    # Opción única (ModelChoiceField devuelve un QuestionOption)
                    if field_value:
                        answer = Answer.objects.create(
                            submission=submission,
                            question=question,
                            organization=organization
                        )
                        answer.selected_options.add(field_value)
                
                elif question.type == Question.QuestionType.MULTI_CHOICE:
                    # Múltiples opciones (ModelMultipleChoiceField devuelve QuerySet)
                    if field_value:
                        answer = Answer.objects.create(
                            submission=submission,
                            question=question,
                            organization=organization
                        )
                        answer.selected_options.set(field_value)
            
            # 3. Procesar la queja (si existe)
            complaint_reason = form.cleaned_data.get('complaint_reason')
            complaint_text = form.cleaned_data.get('complaint_text', '').strip()
            
            if complaint_reason and complaint_text:
                Complaint.objects.create(
                    unit=unit,
                    reason=complaint_reason,
                    text=complaint_text,
                    organization=organization
                )
            
            messages.success(request, '¡Gracias! Tu encuesta ha sido enviada correctamente.')
            
            # Guardar información en la sesión para la vista de agradecimiento
            request.session['has_complaint'] = bool(complaint_reason and complaint_text)
            request.session['submission_success'] = True
            
            # Redirigir a la vista de agradecimiento
            return redirect('interview:thank_you')
            
        except Exception as e:
            messages.error(request, f'Ocurrió un error al procesar la encuesta: {str(e)}')
            print(f'Error en submit_survey: {e}')
            return redirect('interview:survey_form', organization_id=organization_id, unit_id=unit_id)
    else:
        # Si el formulario no es válido, mostrar errores
        messages.error(request, 'Por favor corrige los errores en el formulario.')
        
        # Renderizar el formulario con errores
        questions = Question.objects.filter(
            active=True,
            Organization_id=organization_id
        ).prefetch_related('options').order_by('position')
        
        context = {
            'organization': organization,
            'organization_id': organization_id,
            'unit': unit,
            'unit_id': unit_id,
            'form': form,
            'questions': questions,
            'complaint_reasons': ComplaintReason.objects.filter(
                organization_id=organization_id
            ).order_by('label'),
        }
        return render(request, 'interview/form_section.html', context)


def thank_you(request):
    """
    Vista de agradecimiento mostrada después de enviar la encuesta.
    """
    # Verificar que el usuario acaba de enviar una encuesta
    submission_success = request.session.get('submission_success', False)
    has_complaint = request.session.get('has_complaint', False)
    
    # Limpiar la sesión para evitar accesos directos repetidos
    if 'submission_success' in request.session:
        del request.session['submission_success']
    if 'has_complaint' in request.session:
        del request.session['has_complaint']
    
    # Opcional: obtener estadísticas del día (si quieres mostrarlas)
    from django.utils import timezone
    today = timezone.now().date()
    total_submissions = SurveySubmission.objects.filter(
        submitted_at__date=today
    ).count() if submission_success else 0
    
    context = {
        'has_complaint': has_complaint,
        'show_stats': submission_success,  # Solo mostrar stats si viene de un envío real
        'total_submissions': total_submissions,
    }
    
    return render(request, 'interview/thank_view.html', context)
