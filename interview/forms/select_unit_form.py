from django import forms
from transport.models import Unit


class SelectUnitForm(forms.Form):
    """
    Formulario para seleccionar una unidad de cualquier organización.
    Muestra todas las unidades disponibles con formato "Ruta - Número de unidad".
    """
    
    unit = forms.ModelChoiceField(
        # No cargar unidades a nivel de import; definir queryset en __init__ para evitar
        # consultar toda la tabla innecesariamente cuando se pasa unit_id.
        queryset=Unit.objects.none(),
        required=True,
        empty_label="-- Selecciona la unidad --",
        label="Número de Unidad",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'unit_number'
        })
    )

    def __init__(self, unit_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar el label de cada opción en el select
        self.fields['unit'].label_from_instance = self._get_unit_label
        # Si se pasa unit_id, hacer UNA consulta por esa unidad y limitar el queryset a ella.
        # Si no se pasa, cargar todas las unidades ordenadas.
        if unit_id is not None:
            # Hacemos una única consulta para obtener la unidad (o fallar)
            try:
                unit = Unit.objects.select_related('route').get(pk=unit_id)
            except Unit.DoesNotExist:
                # Validación explícita: id inválido
                raise forms.ValidationError(f"La unidad con id {unit_id} no existe.")

            # Queryset que contiene solo esa unidad (no trae todas primero)
            self.fields['unit'].queryset = Unit.objects.filter(pk=unit.pk).select_related('route')

            # Establecer el valor inicial y deshabilitar el campo para evitar cambios
            # Django preserva el valor inicial en cleaned_data para campos disabled.
            self.initial['unit'] = unit.pk
            self.fields['unit'].disabled = True
            # Asegurar atributos HTML para que se vea consistente
            self.fields['unit'].widget.attrs.update({
                'class': 'form-control',
                'id': 'unit_number',
                'disabled': 'disabled',
            })
        else:
            # Cargar todas las unidades solo cuando no hay unit_id
            self.fields['unit'].queryset = Unit.objects.select_related('route').all().order_by('route__name', 'unit_number')
    
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
