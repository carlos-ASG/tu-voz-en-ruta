from django import forms
from organization.models import Unit


class SelectUnitForm(forms.Form):
    """
    Formulario para seleccionar una unidad de cualquier organización.
    Muestra todas las unidades disponibles con formato "Ruta - Número de unidad".
    """
    
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.select_related('route', 'organization').all().order_by('route__name', 'unit_number'),
        required=True,
        empty_label="-- Selecciona la unidad --",
        label="Número de Unidad",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'unit_number'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar el label de cada opción en el select
        self.fields['unit'].label_from_instance = self._get_unit_label
    
    def _get_unit_label(self, unit):
        """
        Genera el label personalizado para cada unidad en el select.
        Formato: "Ruta: [nombre_ruta] - Unidad [numero]"
        """
        if unit.route:
            return f"Ruta: {unit.route.name} - Unidad {unit.unit_number}"
        else:
            return f"Sin ruta - Unidad {unit.unit_number}"
    
    def get_selected_unit(self):
        """
        Retorna la unidad seleccionada si el formulario es válido.
        """
        if self.is_valid():
            return self.cleaned_data['unit']
        return None
