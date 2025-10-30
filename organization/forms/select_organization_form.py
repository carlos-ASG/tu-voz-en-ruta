from django import forms

from organization.models import Organization


class SelectOrganizationForm(forms.Form):
    """
    Formulario reducido que muestra únicamente las organizaciones por su nombre.
    """

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all().order_by('name'),
        required=True,
        empty_label="-- Selecciona la organización --",
        label="Organización",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'organization_id'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar el nombre tal cual
        self.fields['organization'].label_from_instance = lambda org: org.name

    def get_selected_organization(self):
        """Retorna la organización seleccionada si el formulario es válida."""
        if self.is_valid():
            return self.cleaned_data['organization']
        return None
