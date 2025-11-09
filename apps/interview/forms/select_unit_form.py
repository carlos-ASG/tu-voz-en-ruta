from django import forms
from apps.transport.models import Unit


class SelectUnitForm(forms.Form):
    """
    Formulario para seleccionar una unidad de cualquier organización.
    Muestra todas las unidades disponibles con formato "Ruta - Número de tránsito".
    Busca por transit_number en lugar de por UUID.
    """
    
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.none(),
        required=True,
        empty_label="-- Selecciona la unidad --",
        label="Número de Unidad",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'transit_number'  # ✅ Cambiar id
        })
    )

    def __init__(self, transit_number=None, *args, **kwargs):
        """
        Inicializa el formulario.
        
        Args:
            transit_number: Número de tránsito de la unidad (opcional)
        """
        super().__init__(*args, **kwargs)
        # Personalizar el label de cada opción en el select
        self.fields['unit'].label_from_instance = self._get_unit_label
        
        # Si se pasa transit_number, hacer UNA consulta por ese número
        if transit_number is not None:
            try:
                unit = Unit.objects.select_related('route').get(transit_number=transit_number)
                
                # Queryset que contiene solo esa unidad
                self.fields['unit'].queryset = Unit.objects.filter(pk=unit.pk).select_related('route')

                # Establecer el valor inicial
                self.initial['unit'] = unit.pk
                
                # Cambiar el widget a HiddenInput para que el valor se envíe en POST
                self.fields['unit'].widget = forms.HiddenInput()
                
            except Unit.DoesNotExist:
                # Si la unidad no existe, ignorar el transit_number y mostrar todas las unidades
                self.fields['unit'].queryset = Unit.objects.select_related('route').all().order_by('route__name', 'transit_number')
        else:
            # Cargar todas las unidades ordenadas por ruta y número de tránsito
            self.fields['unit'].queryset = Unit.objects.select_related('route').all().order_by('route__name', 'transit_number')
    
    def _get_unit_label(self, unit):
        """
        Genera el label personalizado para cada unidad en el select.
        Formato: "Ruta: [nombre_ruta] - Unidad [transit_number]"
        """
        if unit.route:
            return f"Ruta: {unit.route.name} - Unidad {unit.transit_number}"
        else:
            return f"Sin ruta - Unidad {unit.transit_number}"
    
    def get_selected_unit(self):
        """
        Retorna la unidad seleccionada si el formulario es válido.
        """
        if self.is_valid():
            return self.cleaned_data['unit']
        return None
