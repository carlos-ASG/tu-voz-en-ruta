from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from transport.models import Unit
from .models import Question, ComplaintReason, SuverySubmission, Answer, Complaint

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def survey_form(request):
    context = {
        'units': Unit.objects.select_related('route').all(),
        'questions': Question.objects.filter(active=True).prefetch_related('options').order_by('position'),
        'complaint_reasons': ComplaintReason.objects.all().order_by('label'),
    }
    return render(request, 'interview/form_section.html', context)

def submit_survey(request):
    if request.method == 'POST':
        try:
            # 1. Obtener la unidad seleccionada
            unit_id = request.POST.get('unit_number')
            if not unit_id:
                messages.error(request, 'Debe seleccionar una unidad.')
                return redirect('interview:survey_form')
            
            unit = Unit.objects.get(id=unit_id)
            
            # 2. Crear el registro de envío de encuesta
            submission = SuverySubmission.objects.create(unit=unit)
            
            # 3. Procesar las respuestas a las preguntas
            questions = Question.objects.filter(active=True)
            for question in questions:
                question_id_str = str(question.id)
                
                if question.type == Question.QuestionType.RATING:
                    # Buscar campo tipo question_<uuid>_rating
                    rating_key = f'question_{question_id_str}_rating'
                    rating_value = request.POST.get(rating_key)
                    if rating_value:
                        Answer.objects.create(
                            submission=submission,
                            question=question,
                            rating_answer=int(rating_value)
                        )
                
                elif question.type == Question.QuestionType.TEXT:
                    # Buscar campo tipo question_<uuid>_text
                    text_key = f'question_{question_id_str}_text'
                    text_value = request.POST.get(text_key)
                    if text_value and text_value.strip():
                        Answer.objects.create(
                            submission=submission,
                            question=question,
                            text_answer=text_value.strip()
                        )
                
                elif question.type == Question.QuestionType.CHOICE:
                    # Buscar campo tipo question_<uuid>_choice (radio button)
                    choice_key = f'question_{question_id_str}_choice'
                    option_id = request.POST.get(choice_key)
                    if option_id:
                        answer = Answer.objects.create(
                            submission=submission,
                            question=question
                        )
                        answer.selected_options.add(option_id)
                
                elif question.type == Question.QuestionType.MULTI_CHOICE:
                    # Buscar campos tipo question_<uuid>_multi (checkboxes - puede haber múltiples)
                    multi_key = f'question_{question_id_str}_multi'
                    option_ids = request.POST.getlist(multi_key)
                    if option_ids:
                        answer = Answer.objects.create(
                            submission=submission,
                            question=question
                        )
                        answer.selected_options.set(option_ids)
            
            # 4. Procesar la queja (si existe)
            complaint_reason_id = request.POST.get('complaint_reason')
            complaint_text = request.POST.get('complaint_text', '').strip()
            
            if complaint_reason_id and complaint_text:
                complaint_reason = ComplaintReason.objects.get(id=complaint_reason_id)
                Complaint.objects.create(
                    unit=unit,
                    reason=complaint_reason,
                    text=complaint_text
                )
            
            messages.success(request, '¡Gracias! Tu encuesta ha sido enviada correctamente.')
            
        except Unit.DoesNotExist:
            messages.error(request, 'La unidad seleccionada no existe.')
        except ComplaintReason.DoesNotExist:
            messages.error(request, 'El motivo de queja seleccionado no existe.')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al procesar la encuesta: {str(e)}')
            print(f'Error en submit_survey: {e}')
    
    return redirect('interview:survey_form')
