from django import forms
from transport.models import Unit


class QRGeneratorForm(forms.Form):
    """
    Formulario para seleccionar unidades y generar códigos QR en masa.
    """
    
    SELECTION_CHOICES = [
        ('all', 'Todas las unidades'),
        ('single', 'Una unidad específica'),
        ('range', 'Rango de unidades'),
    ]
    
    selection_type = forms.ChoiceField(
        choices=SELECTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'selection-radio'}),
        label='Selecciona el tipo de generación',
        initial='all'
    )
    
    # Para selección única
    single_unit = forms.ModelChoiceField(
        queryset=Unit.objects.none(),
        required=False,
        empty_label="-- Selecciona una unidad --",
        label="Unidad",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'singleUnitSelect'})
    )
    
    # Para rango de unidades
    start_unit = forms.ModelChoiceField(
        queryset=Unit.objects.none(),
        required=False,
        empty_label="-- Unidad inicial --",
        label="Desde",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'startUnitSelect'})
    )
    
    end_unit = forms.ModelChoiceField(
        queryset=Unit.objects.none(),
        required=False,
        empty_label="-- Unidad final --",
        label="Hasta",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'endUnitSelect'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar todas las unidades ordenadas por transit_number
        units_qs = Unit.objects.select_related('route').order_by('transit_number')
        
        self.fields['single_unit'].queryset = units_qs
        self.fields['start_unit'].queryset = units_qs
        self.fields['end_unit'].queryset = units_qs
        
        # Personalizar el label de cada unidad
        self.fields['single_unit'].label_from_instance = self._get_unit_label
        self.fields['start_unit'].label_from_instance = self._get_unit_label
        self.fields['end_unit'].label_from_instance = self._get_unit_label
    
    def _get_unit_label(self, unit):
        """Genera el label personalizado para cada unidad en el select."""
        if unit.route:
            return f"{unit.transit_number} - Ruta: {unit.route.name}"
        else:
            return f"{unit.transit_number} - Sin ruta"
    
    def clean(self):
        cleaned_data = super().clean()
        selection_type = cleaned_data.get('selection_type')
        
        if selection_type == 'single':
            if not cleaned_data.get('single_unit'):
                raise forms.ValidationError('Debes seleccionar una unidad.')
        
        elif selection_type == 'range':
            start_unit = cleaned_data.get('start_unit')
            end_unit = cleaned_data.get('end_unit')
            
            if not start_unit or not end_unit:
                raise forms.ValidationError('Debes seleccionar ambas unidades para el rango.')
            
            # Validar que el rango sea válido (comparar transit_number)
            if start_unit.transit_number > end_unit.transit_number:
                raise forms.ValidationError('La unidad inicial debe ser menor o igual que la unidad final.')
        
        return cleaned_data
    
    def get_selected_units(self):
        """
        Retorna el queryset de unidades seleccionadas según el tipo de selección.
        """
        if not self.is_valid():
            return Unit.objects.none()
        
        selection_type = self.cleaned_data['selection_type']
        
        if selection_type == 'all':
            return Unit.objects.select_related('route').order_by('transit_number')
        
        elif selection_type == 'single':
            unit = self.cleaned_data['single_unit']
            return Unit.objects.filter(pk=unit.pk).select_related('route')
        
        elif selection_type == 'range':
            start_unit = self.cleaned_data['start_unit']
            end_unit = self.cleaned_data['end_unit']
            
            # Filtrar unidades en el rango (comparando transit_number como strings)
            return Unit.objects.filter(
                transit_number__gte=start_unit.transit_number,
                transit_number__lte=end_unit.transit_number
            ).select_related('route').order_by('transit_number')
        
        return Unit.objects.none()
