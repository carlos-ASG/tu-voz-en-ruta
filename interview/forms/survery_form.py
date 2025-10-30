

from django import forms
from ..models import Question


class SurveyForm(forms.Form):
    """
    Formulario dinámico para las preguntas de la encuesta.
    Genera campos automáticamente según las preguntas activas.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario con preguntas dinámicas.
        """
        super().__init__(*args, **kwargs)
        
        # Obtener preguntas activas ordenadas por posición
        questions = Question.objects.filter(
            active=True,
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
                        'name': f'question_{question.id}'
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
                    })
                )
            
            # Guardar metadata de la pregunta para uso en el template
            self.fields[field_name].question_type = question.type
            self.fields[field_name].question_id = question.id
            self.fields[field_name].question_obj = question
    
    def get_questions_data(self):
        """
        Retorna información estructurada de las preguntas para renderizado.
        
        Returns:
            Lista de diccionarios con información de cada pregunta
        """
        questions_data = []
        for field_name, field_obj in self.fields.items():
            if field_name.startswith('question_'):
                questions_data.append({
                    'field_name': field_name,
                    'field': self[field_name],  # BoundField renderizable
                    'question_id': getattr(field_obj, 'question_id', None),
                    'question_type': getattr(field_obj, 'question_type', None),
                    'question_obj': getattr(field_obj, 'question_obj', None),
                })
        return questions_data