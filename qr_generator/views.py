from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from io import BytesIO
import zipfile
import qrcode

from .forms import QRGeneratorForm


def qr_generator_view(request):
    """
    Vista principal del generador de códigos QR.
    Muestra el formulario de selección de unidades.
    """
    form = QRGeneratorForm()
    
    context = {
        'form': form,
        'title': 'Generador de Códigos QR',
    }
    
    return render(request, 'qr_generator/qr_generator_template.html', context)


def generate_qr_codes(request):
    """
    Genera códigos QR para las unidades seleccionadas.
    Si es una unidad: retorna la imagen QR directamente.
    Si son múltiples: retorna un archivo ZIP con todos los QR.
    """
    if request.method != 'POST':
        return redirect('qr_generator:qr_generator')
    
    form = QRGeneratorForm(request.POST)
    
    if not form.is_valid():
        # Si el formulario no es válido, volver a mostrar con errores
        context = {
            'form': form,
            'title': 'Generador de Códigos QR',
        }
        return render(request, 'qr_generator/qr_generator_template.html', context)
    
    # Obtener las unidades seleccionadas
    units = form.get_selected_units()
    
    if not units.exists():
        messages.error(request, 'No se encontraron unidades para generar códigos QR.')
        return redirect('qr_generator:qr_generator')
    
    # Obtener información del tenant para construir las URLs
    tenant = request.tenant
    domain = tenant.get_primary_domain()
    
    if not domain:
        messages.error(request, 'No se pudo obtener el dominio del tenant.')
        return redirect('qr_generator:qr_generator')
    
    # Si es una sola unidad, retornar la imagen directamente
    if units.count() == 1:
        unit = units.first()
        qr_image = generate_qr_image(unit, domain.domain)
        
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="QR_{unit.transit_number}.png"'
        qr_image.save(response, 'PNG')
        return response
    
    # Si son múltiples unidades, crear un ZIP
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for unit in units:
            qr_image = generate_qr_image(unit, domain.domain)
            
            # Guardar la imagen en un buffer temporal
            img_buffer = BytesIO()
            qr_image.save(img_buffer, 'PNG')
            img_buffer.seek(0)
            
            # Agregar al ZIP con nombre descriptivo
            filename = f"QR_{unit.transit_number}"
            if unit.route:
                filename += f"_Ruta_{unit.route.name}"
            filename += ".png"
            
            zip_file.writestr(filename, img_buffer.getvalue())
    
    # Preparar respuesta con el ZIP
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="QR_Codes_{tenant.schema_name}.zip"'
    
    return response


def generate_qr_image(unit, domain):
    """
    Genera una imagen QR para una unidad específica.
    
    Args:
        unit: Instancia de Unit
        domain: Dominio del tenant (ej: 'alianza.tuvozenruta.com')
    
    Returns:
        PIL.Image: Imagen del código QR
    """
    # Construir la URL completa para la encuesta de esta unidad
    # Formato: http://alianza.tuvozenruta.com:8000/interview/?transit_number=ABC123
    url = f"http://{domain}:8000/interview/?transit_number={unit.transit_number}"
    
    # Crear el código QR
    qr = qrcode.QRCode(
        version=1,  # Tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
        box_size=10,  # Tamaño de cada "caja" del QR
        border=4,  # Grosor del borde
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    # Generar la imagen (PIL Image)
    img = qr.make_image(fill_color="black", back_color="white")
    
    return img
