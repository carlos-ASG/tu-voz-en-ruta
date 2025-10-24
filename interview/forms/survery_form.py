from django import forms
from ..models import Question, QuestionOption, ComplaintReason, Answer
from organization.models import Unit


class SurveyForm(forms.Form):
    """
    Formulario dinámico para encuestas de satisfacción.
    Genera campos automáticamente según las preguntas activas de una organización.
    """
    
    complaint_reason = forms.ModelChoiceField(
        queryset=ComplaintReason.objects.none(),
        required=False,
        empty_label="-- Selecciona un motivo (opcional) --",
        label="Motivo de la queja",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'complaint_reason'})
    )
    
    complaint_text = forms.CharField(
        required=False,
        label="Describe tu queja o sugerencia",
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control textarea-input complaint-textarea',
            'rows': 5,
            'id': 'complaint_text',
            'placeholder': 'Describe detalladamente tu queja o sugerencia...',
            'maxlength': 1000
        })
    )
    
    def __init__(self, organization_id, *args, **kwargs):
        """
        Inicializa el formulario con preguntas dinámicas basadas en la organización.
        
        Args:
            organization_id: UUID de la organización para filtrar preguntas y opciones
        """
        super().__init__(*args, **kwargs)
        
        # Filtrar complaint reasons por organización
        self.fields['complaint_reason'].queryset = ComplaintReason.objects.filter(
            organization_id=organization_id
        ).order_by('label')
        
        # Obtener preguntas activas de la organización ordenadas por posición
        questions = Question.objects.filter(
            active=True,
            Organization_id=organization_id
        ).prefetch_related('options').order_by('position')
        
        # Crear campos dinámicamente según el tipo de pregunta
        for question in questions:
            field_name = f'question_{question.id}'
            
            if question.type == Question.QuestionType.RATING:
                # Campo oculto para rating (las estrellas actualizan este campo via JavaScript)
                self.fields[field_name] = forms.IntegerField(
                    required=True,
                    min_value=1,
                    max_value=5,
                    label=question.text,
                    widget=forms.HiddenInput(attrs={
                        'id': f'rating_{question.id}',
                        'name': f'question_{question.id}_rating'
                    })
                )
            
            elif question.type == Question.QuestionType.TEXT:
                # Campo de texto libre
                self.fields[field_name] = forms.CharField(
                    required=True,
                    label=question.text,
                    max_length=1000,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control textarea-input',
                        'rows': 3,
                        'id': f'text_{question.id}',
                        'name': f'question_{question.id}_text',
                        'placeholder': 'Escribe tu respuesta aquí...'
                    })
                )
            
            elif question.type == Question.QuestionType.CHOICE:
                # Opción única (radio buttons)
                options = question.options.all().order_by('position')
                self.fields[field_name] = forms.ModelChoiceField(
                    queryset=options,
                    required=False,
                    label=question.text,
                    widget=forms.RadioSelect(attrs={
                        'class': 'radio-options',
                        'name': f'question_{question.id}_choice'
                    }),
                    empty_label=None
                )
            
            elif question.type == Question.QuestionType.MULTI_CHOICE:
                # Múltiples opciones (checkboxes)
                options = question.options.all().order_by('position')
                self.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=options,
                    required=False,
                    label=question.text,
                    widget=forms.CheckboxSelectMultiple(attrs={
                        'class': 'checkbox-options',
                        'name': f'question_{question.id}_multichoice'
                    })
                )
            
            # Guardar metadata de la pregunta para uso en el template
            self.fields[field_name].question_type = question.type
            self.fields[field_name].question_id = question.id
    
    def get_questions_data(self):
        """
        Retorna información estructurada de las preguntas para renderizado en el template.
        
        Returns:
            Lista de diccionarios con información de cada pregunta
        """
        questions_data = []
        for field_name, field in self.fields.items():
            if field_name.startswith('question_'):
                questions_data.append({
                    'field_name': field_name,
                    'field': field,
                    'question_id': getattr(field, 'question_id', None),
                    'question_type': getattr(field, 'question_type', None),
                })
        return questions_data
    
    def clean(self):
        """
        Validación adicional del formulario.
        """
        cleaned_data = super().clean()
        
        # Validar que si hay complaint_text, debe haber complaint_reason
        complaint_text = cleaned_data.get('complaint_text', '').strip()
        complaint_reason = cleaned_data.get('complaint_reason')
        
        if complaint_text and not complaint_reason:
            self.add_error('complaint_reason', 
                          'Debe seleccionar un motivo si va a ingresar una queja.')
        
        return cleaned_data
