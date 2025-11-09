from django import forms
from ..models import ComplaintReason


class ComplaintForm(forms.Form):
    """
    Formulario para quejas y sugerencias.
    Solo maneja la sección de quejas (sin preguntas de encuesta).
    """
    
    complaint_reason = forms.ModelChoiceField(
        queryset=ComplaintReason.objects.none(),
        required=False,
        empty_label="-- Selecciona un motivo (opcional) --",
        label="Motivo de la queja",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'complaint_reason'
        })
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
            'maxlength': '1000',
            # Mantener readonly por defecto; el JS en la plantilla habilita el campo
            'readonly': 'readonly',
            # data attribute para identificarlo desde JS
            'data-toggle-by': 'complaint_reason'
        }),
        help_text='Tu queja será revisada y procesada para mejorar el servicio. Máximo 1000 caracteres.'
    )

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario de quejas.
        """
        super().__init__(*args, **kwargs)
        
        # Cargar todos los motivos de queja ordenados
        self.fields['complaint_reason'].queryset = ComplaintReason.objects.all().order_by('label')
    
    def clean(self):
        """
        Validación: si hay texto de queja, debe haber un motivo seleccionado.
        """
        cleaned_data = super().clean()
        
        complaint_text = cleaned_data.get('complaint_text', '').strip()
        complaint_reason = cleaned_data.get('complaint_reason')
        
        if complaint_text and not complaint_reason:
            self.add_error('complaint_reason', 
                          'Debe seleccionar un motivo si va a ingresar una queja.')
        
        return cleaned_data
