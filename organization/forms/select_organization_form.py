from django import forms

from organization.models import Organization
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class SelectOrganizationForm(forms.Form):
    """
    Formulario reducido que muestra únicamente las organizaciones por su nombre.
    """

    organization = forms.ModelChoiceField(
        queryset=Organization.objects.exclude(schema_name='public').order_by('name'),
        required=True,
        empty_label="-- Selecciona la organización --",
        label="Organización",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'organization_id'
        })
    )
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox,
        label='Verificación',
        error_messages={
            'required': 'Por favor completa la verificación reCAPTCHA.',
            'invalid': 'Error en la verificación reCAPTCHA. Por favor intenta de nuevo.'
        }
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
