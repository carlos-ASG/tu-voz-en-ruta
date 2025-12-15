import http
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from apps.organization.forms.select_organization_form import SelectOrganizationForm
from apps.organization.models import Domain
from apps.organization.utils import build_tenant_url


# Create your views here.
def select_organization(request):
    """
    Vista para seleccionar la organización antes de mostrar el formulario de encuesta.
    Muestra todas las organizaciones disponibles.
    Al enviar, redirige automáticamente al subdominio de la organización seleccionada.
    """
    if request.method != 'POST':
        # GET: mostrar formulario vacío
        form = SelectOrganizationForm()
        context = {'form': form}
        return render(request, 'organization/select_organization.html', context)

    form = SelectOrganizationForm(request.POST)
    if form.is_valid():
        organization = form.get_selected_organization()
        
        # Obtener el dominio principal del tenant (organización)
        try:
            # Buscar el dominio primario de la organización
            domain = Domain.objects.get(tenant=organization, is_primary=True)

            # Construir la URL completa con el esquema y el dominio del tenant
            # Redirigir a la vista de selección de unidad para mostrar la encuesta
            scheme = 'https' if request.is_secure() else 'http'
            port = request.get_port()
            tenant_url = build_tenant_url(scheme, domain.domain, port=port, path='/survey')

            # Redirigir al subdominio del tenant
            return HttpResponseRedirect(tenant_url)
            
        except Domain.DoesNotExist:
            # Si no existe dominio para la organización, mostrar error
            form.add_error('organization', 
                          'La organización seleccionada no tiene un dominio configurado.')
            context = {'form': form}
            return render(request, 'organization/select_organization.html', context)
    else:
        # Si el formulario no es válido, volver a mostrar con errores
        context = {'form': form}
        return render(request, 'organization/select_organization.html', context)
    

def index(request):
    return HttpResponse(f"<h1>index publico</h1>")
