from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django_ratelimit.core import is_ratelimited

from apps.transport.models import Unit
from .models import Question, ComplaintReason, SurveySubmission, Answer, Complaint
from .forms.complaint_form import ComplaintForm
from .forms.select_unit_form import SelectUnitForm
from .forms.survery_form import SurveyForm


def select_unit_for_survey(request):
    """
    Vista intermedia para seleccionar una unidad antes de mostrar la encuesta.

    Comportamiento:
    - Si hay solo 1 unidad: redirije automáticamente a su encuesta
    - Si hay múltiples unidades: muestra un selector
    - Si no hay unidades: muestra mensaje de error
    """
    # Obtener todas las unidades disponibles (automáticamente filtradas por tenant)
    units = Unit.objects.all().order_by('transit_number')
    unit_count = units.count()

    # Caso 1: No hay unidades disponibles
    if unit_count == 0:
        messages.warning(request, 'No hay unidades disponibles en este momento.')
        return render(request, 'interview/no_units.html')

    # Caso 2: Solo hay una unidad - redirigir automáticamente
    if unit_count == 1:
        first_unit = units.first()
        return redirect('interview:survey_form', transit_number=first_unit.transit_number)

    # Caso 3: Hay múltiples unidades - procesar selección
    if request.method == 'POST':
        selected_transit_number = request.POST.get('unit_transit_number')
        if selected_transit_number:
            # Verificar que la unidad existe
            if units.filter(transit_number=selected_transit_number).exists():
                return redirect('interview:survey_form', transit_number=selected_transit_number)
            else:
                messages.error(request, 'La unidad seleccionada no existe.')

    # Mostrar selector de unidades
    context = {
        'units': units,
        'unit_count': unit_count,
    }
    return render(request, 'interview/select_unit.html', context)


def get_ratelimit_key_ip_and_unit(group, request):
    """
    Función personalizada para generar la clave de rate limiting.
    Combina la IP del usuario con el ID de la unidad para permitir
    que un mismo usuario envíe encuestas a diferentes unidades.

    Retorna: 'ip:unit_id' (ej: '192.168.1.1:uuid-de-unidad')
    """
    # Obtener la IP del usuario (considerando proxies)
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or \
         request.META.get('REMOTE_ADDR', '')

    # Obtener el ID de la unidad desde POST
    unit_pk = request.POST.get('unit', 'unknown')

    # Combinar IP + unit_pk para crear una clave única
    return f"{ip}:{unit_pk}"


def survey_form(request, transit_number):
    """
    Vista para mostrar el formulario de encuesta con preguntas dinámicas.
    Maneja tres formularios separados: selección de unidad, preguntas de encuesta y quejas.

    Args:
        transit_number (str): Número de tránsito de la unidad (requerido en la URL)
    """
    # Validar que la unidad existe
    try:
        unit = Unit.objects.get(transit_number=transit_number)
    except Unit.DoesNotExist:
        messages.error(request, f'La unidad con número de tránsito "{transit_number}" no existe.')
        # Redirigir a una página de error o inicio
        from django.http import Http404
        raise Http404(f'Unidad {transit_number} no encontrada')

    # Inicializar los tres formularios
    # El transit_number ya está validado, así que pasamos el objeto unit directamente
    unit_form = SelectUnitForm(transit_number=transit_number, data=request.POST or None)
    survey_form_obj = SurveyForm(data=request.POST or None)
    complaint_form = ComplaintForm(data=request.POST or None)

    context = {
        'transit_number': transit_number,
        'unit': unit,  # Agregar el objeto unit al contexto
        'unit_form': unit_form,
        'survey_form': survey_form_obj,
        'complaint_form': complaint_form,
    }

    return render(request, 'interview/form_section.html', context)


def submit_survey(request, transit_number):
    """
    Vista para procesar el envío de la encuesta.
    Valida y procesa los tres formularios: unidad, encuesta y quejas.
    El aislamiento por organización es automático gracias al schema del tenant (django-tenants).

    Args:
        transit_number (str): Número de tránsito de la unidad (requerido en la URL)

    Rate Limiting: 1 petición por combinación de IP + unidad cada 15 minutos.
    Esto permite que un usuario envíe encuestas a diferentes unidades sin restricción,
    pero evita spam múltiple a la misma unidad.
    IMPORTANTE: El rate limit solo se incrementa DESPUÉS de validar los formularios,
    para evitar bloquear usuarios que cometen errores (ej: no completar reCAPTCHA).
    """
    if request.method != 'POST':
        return redirect('interview:survey_form', transit_number=transit_number)

    # Validar que la unidad existe (buscar por transit_number)
    unit = get_object_or_404(Unit, transit_number=transit_number)

    # Inicializar los tres formularios con los datos POST
    # Pasar transit_number para que el formulario sepa que ya hay una unidad seleccionada
    unit_form = SelectUnitForm(transit_number=unit.transit_number, data=request.POST)
    survey_form = SurveyForm(data=request.POST)
    complaint_form = ComplaintForm(data=request.POST)

    # Validar todos los formularios (incluyendo reCAPTCHA)
    unit_valid = unit_form.is_valid()
    survey_valid = survey_form.is_valid()
    complaint_valid = complaint_form.is_valid()

    if not (unit_valid and survey_valid and complaint_valid):
        # Si algún formulario no es válido (incluyendo reCAPTCHA),
        # NO incrementar el rate limit y mostrar errores
        messages.error(request, 'Por favor corrige los errores en el formulario.')

        context = {
            'transit_number': unit.transit_number,
            'unit': unit,
            'unit_form': unit_form,
            'survey_form': survey_form,
            'complaint_form': complaint_form,
        }
        return render(request, 'interview/form_section.html', context)

    # ============================================
    # FORMULARIOS VÁLIDOS - VERIFICAR RATE LIMIT
    # ============================================
    # Solo verificar e incrementar el rate limit DESPUÉS de que los formularios sean válidos
    limited = is_ratelimited(
        request=request,
        group='submit_survey',
        fn=None,
        key=get_ratelimit_key_ip_and_unit,
        rate='1/15m',
        method='POST',
        increment=True  # Incrementar el contador SOLO si está válido
    )

    if limited:
        messages.error(
            request,
            f'Has enviado una encuesta para la unidad {unit.transit_number} recientemente. '
            'Por favor espera 15 minutos antes de enviar otra para esta unidad.'
        )
        return redirect('interview:survey_form', transit_number=transit_number)
    
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
            'transit_number': unit.transit_number,
            'unit': unit,
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
