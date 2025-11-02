# Generador de Códigos QR

Aplicación para generar códigos QR en masa para las encuestas de unidades de transporte.

## Características

- ✅ **Generación masiva**: Genera QR para todas las unidades, una específica o un rango
- ✅ **Sin almacenamiento**: Los QR se generan en memoria y se envían directamente al navegador
- ✅ **Compresión automática**: Múltiples QR se comprimen en un archivo ZIP
- ✅ **URLs dinámicas**: Cada QR apunta a la encuesta con el `transit_number` preseleccionado

## Uso

### Acceso

Desde el admin del tenant, accede a:
```
http://[tenant].tuvozenruta.com:8000/qr-generator/
```

O agrega un enlace directo en el admin.

### Opciones de generación

1. **Todas las unidades**: Genera QR para todas las unidades registradas (descarga ZIP)
2. **Una unidad específica**: Genera QR para una sola unidad (descarga PNG)
3. **Rango de unidades**: Genera QR para unidades entre dos números de tránsito (descarga ZIP)

### Formato de los QR

Cada código QR contiene una URL con el formato:
```
http://[tenant].tuvozenruta.com:8000/interview/?transit_number=[NUMERO]
```

Cuando un usuario escanea el QR, el formulario de encuesta:
- Preselecciona automáticamente la unidad correspondiente
- Muestra la información de la ruta asociada
- El usuario solo necesita completar las preguntas

### Nombres de archivos

- **Unidad única**: `QR_[transit_number].png`
- **Múltiples unidades**: `QR_Codes_[schema_name].zip`
  - Contenido: `QR_[transit_number]_Ruta_[nombre_ruta].png`

## Dependencias

- `qrcode[pil]`: Generación de códigos QR con soporte para imágenes PIL

## Estructura técnica

```
qr_generator/
├── forms.py              # Formulario de selección de unidades
├── views.py              # Lógica de generación y descarga
├── urls.py               # Rutas de la app
├── templates/
│   └── qr_generator/
│       └── qr_generator_template.html  # Interfaz principal
└── static/
    └── qr_generator/
        ├── css/
        │   └── style.css       # Estilos del formulario
        └── js/
            └── script.js       # Lógica de visibilidad de secciones
```

## Notas técnicas

- Los QR se generan en memoria usando `BytesIO` (no se guardan en disco)
- La compresión ZIP también se hace en memoria
- El nivel de corrección de errores es **HIGH** (permite hasta 30% de daño)
- Tamaño del QR: `box_size=10`, `border=4`

## Integración con el admin

Para agregar un enlace directo en el admin, edita `transport/admin.py`:

```python
class TenantAdminSite(admin.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context['qr_generator_url'] = reverse('qr_generator:qr_generator')
        return context
```

Y en el template del admin:
```html
<a href="{% url 'qr_generator:qr_generator' %}">Generar Códigos QR</a>
```
