from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from io import BytesIO
import zipfile
import qrcode
import re
from PIL import Image, ImageDraw, ImageFont

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
    tenant = request.tenant.schema_name
    
    if not tenant:
        messages.error(request, 'No se pudo obtener el tenant.')
        return redirect('qr_generator:qr_generator')
    
    # Helper para sanitizar nombres de archivo
    def _safe_filename(s: str) -> str:
        s = str(s)
        # Reemplaza caracteres no permitidos por '_' (mantiene letras, números, guiones, puntos y guion bajo)
        return re.sub(r'[^A-Za-z0-9._-]', '_', s)

    # Si es una sola unidad, retornar la imagen directamente
    if units.count() == 1:
        unit = units.first()
        qr_image = generate_qr_image(unit, tenant)

        response = HttpResponse(content_type='image/png')
        filename = f"{_safe_filename(unit.transit_number)}.png"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        qr_image.save(response, 'PNG')
        return response
    
    # Si son múltiples unidades, crear un ZIP
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for unit in units:
            qr_image = generate_qr_image(unit, tenant)

            # Guardar la imagen en un buffer temporal
            img_buffer = BytesIO()
            qr_image.save(img_buffer, 'PNG')
            img_buffer.seek(0)

            # Agregar al ZIP usando únicamente el transit_number (sanitizado)
            filename = f"{_safe_filename(unit.transit_number)}.png"
            zip_file.writestr(filename, img_buffer.getvalue())
    
    # Preparar respuesta con el ZIP
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    # tenant es una cadena (schema_name) — usarla directamente
    response['Content-Disposition'] = f'attachment; filename="QR_Codes_{tenant}.zip"'
    
    return response


def generate_qr_image(unit, tenant):
    """
    Genera una imagen QR para una unidad específica con un encabezado que muestra
    el número de tránsito.

    Args:
        unit: Instancia de Unit
        tenant: Schema name del tenant (ej: 'alianza')

    Returns:
        PIL.Image: Imagen del código QR con encabezado
    """
    # Construir la URL completa para la encuesta de esta unidad
    # Formato: http://alianza.tuvozenruta.com/interview/?transit_number=ABC123
    url = f"http://{tenant}.tuvozenruta.com/interview/?transit_number={unit.transit_number}"

    # Crear el código QR
    qr = qrcode.QRCode(
        version=1,  # Tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
        box_size=10,  # Tamaño de cada "caja" del QR
        border=4,  # Grosor del borde
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Generar la imagen QR base
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Convertir a RGB si es necesario (para poder agregar texto)
    if qr_img.mode != 'RGB':
        qr_img = qr_img.convert('RGB')

    # Obtener dimensiones del QR
    qr_width, qr_height = qr_img.size

    # Configuración del encabezado
    header_height = 80  # Altura del encabezado

    # Crear una nueva imagen con espacio para el encabezado
    total_height = header_height + qr_height
    final_img = Image.new('RGB', (qr_width, total_height), 'white')

    # Dibujar el encabezado
    draw = ImageDraw.Draw(final_img)

    # Intentar usar una fuente del sistema, si no está disponible usar la predeterminada
    try:
        # Tamaño de fuente para el título
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
    except:
        try:
            # Alternativa para Linux
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            # Si no hay fuentes disponibles, usar la predeterminada
            font_title = ImageFont.load_default()

    # Texto del encabezado (solo el número de tránsito)
    title_text = unit.transit_number

    # Calcular posiciones para centrar el texto
    try:
        # Método moderno de Pillow
        title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
    except:
        # Método legacy si textbbox no está disponible
        title_width = len(title_text) * 20

    title_x = (qr_width - title_width) // 2

    # Centrar verticalmente el título en el encabezado
    title_y = (header_height - 36) // 2  # 36 es el tamaño de fuente del título

    # Dibujar el texto del encabezado
    draw.text((title_x, title_y), title_text, fill='black', font=font_title)

    # Pegar el código QR debajo del encabezado
    final_img.paste(qr_img, (0, header_height))

    return final_img
