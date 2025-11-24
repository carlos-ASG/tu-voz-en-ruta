# Monitoreo con Sentry

Este documento describe la configuración y uso de Sentry para el monitoreo de errores, rendimiento y logs en el sistema multi-tenant "Tu Voz en Ruta".

## Tabla de Contenidos

- [Configuración](#configuración)
- [Características Habilitadas](#características-habilitadas)
- [Contexto Multi-tenant](#contexto-multi-tenant)
- [Uso en Desarrollo](#uso-en-desarrollo)
- [Uso en Producción](#uso-en-producción)
- [Captura Manual de Errores](#captura-manual-de-errores)
- [Mejores Prácticas](#mejores-prácticas)
- [Troubleshooting](#troubleshooting)

## Configuración

### Variables de Entorno

La integración con Sentry requiere las siguientes variables de entorno:

```bash
# DSN de tu proyecto en Sentry
SENTRY_DSN=https://your-key@o1234567.ingest.us.sentry.io/1234567

# Entorno de ejecución (development, staging, production)
SENTRY_ENVIRONMENT=production
```

### Configuración en settings.py

La configuración de Sentry se encuentra en [buzon_quejas/settings.py:28-54](buzon_quejas/settings.py#L28-L54):

```python
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        send_default_pii=True,
        enable_logs=True,
        traces_sample_rate=1.0 if SENTRY_ENVIRONMENT == "development" else 0.2,
        profiles_sample_rate=1.0 if SENTRY_ENVIRONMENT == "development" else 0.2,
    )
```

### Obtener el DSN

1. Crear cuenta en [sentry.io](https://sentry.io)
2. Crear un nuevo proyecto de tipo "Django"
3. Copiar el DSN desde **Settings** → **Projects** → *[Tu Proyecto]* → **Client Keys (DSN)**
4. Agregar el DSN al archivo `.env` del proyecto

## Características Habilitadas

### 1. Captura Automática de Errores

Sentry captura automáticamente:
- **Excepciones no manejadas** en vistas y middleware
- **Errores 500** en respuestas HTTP
- **Errores de base de datos** (queries fallidas)
- **Errores de template** (variables no definidas, tags inválidos)

### 2. Performance Monitoring

La integración captura métricas de rendimiento:

- **Transactions**: Cada request HTTP se registra como una transacción
- **Database queries**: Tiempo de ejecución de queries SQL
- **Template rendering**: Tiempo de renderizado de templates
- **HTTP requests externos**: Llamadas a APIs de terceros

**Sampling rates configurados:**
- **Development**: 100% de transacciones (para debugging completo)
- **Production**: 20% de transacciones (para controlar costos)

### 3. Profiling

Habilitado automáticamente cuando hay transacciones activas:

- **CPU usage**: Uso de CPU por función
- **Memory allocation**: Asignación de memoria
- **Call stacks**: Stack traces de ejecución

**Sampling rates:**
- **Development**: 100% de sesiones
- **Production**: 20% de sesiones

### 4. Logs Integration

Todos los logs de Django se envían a Sentry:

```python
import logging

logger = logging.getLogger(__name__)
logger.error("Error procesando encuesta", extra={"survey_id": survey_id})
```

## Contexto Multi-tenant

### Identificación de Tenants

Para identificar qué tenant generó un error, se recomienda usar el middleware personalizado o tags de Sentry:

```python
from sentry_sdk import set_tag, set_context

# En el middleware TenantActiveMiddleware o en vistas
def process_request(self, request):
    if hasattr(request, 'tenant'):
        set_tag("tenant_schema", request.tenant.schema_name)
        set_tag("tenant_name", request.tenant.name)
        set_context("tenant", {
            "id": str(request.tenant.id),
            "name": request.tenant.name,
            "schema": request.tenant.schema_name,
            "is_active": request.tenant.is_active,
        })
```

### Filtrado en Sentry Dashboard

Una vez configurado, podrás filtrar errores por tenant:

- En el dashboard de Sentry, usar el filtro: `tenant_schema:cliente1`
- Crear alertas específicas por tenant
- Generar reportes separados por organización

## Uso en Desarrollo

### Configuración Local

1. Copiar `.env-example` a `.env`:
   ```bash
   cp .env-example .env
   ```

2. Configurar las variables:
   ```bash
   SENTRY_DSN=https://your-dev-dsn@sentry.io/your-project
   SENTRY_ENVIRONMENT=development
   ```

3. Sentry capturará todos los errores, incluso en DEBUG=True

### Probar la Integración

Crear una vista de prueba para verificar que Sentry funciona:

```python
# En cualquier urls.py (temporal)
def trigger_error(request):
    1 / 0  # Genera ZeroDivisionError

urlpatterns = [
    path('sentry-test/', trigger_error),
]
```

Visitar `/sentry-test/` y verificar que el error aparece en el dashboard de Sentry.

## Uso en Producción

### Configuración en Railway/Render

1. Agregar las variables de entorno en el panel de Railway/Render:
   ```
   SENTRY_DSN=https://your-prod-dsn@sentry.io/your-project
   SENTRY_ENVIRONMENT=production
   ```

2. Hacer deploy del proyecto

3. Verificar que los errores se reportan en el dashboard de Sentry

### Releases y Source Maps

Para asociar errores con versiones específicas del código:

```bash
# Durante el deploy (en build.sh o CI/CD)
export SENTRY_RELEASE=$(git rev-parse HEAD)

# En settings.py
sentry_sdk.init(
    dsn=SENTRY_DSN,
    release=os.getenv("SENTRY_RELEASE"),
    ...
)
```

### Notificaciones

Configurar alertas en Sentry:

1. **Settings** → **Alerts** → **Create Alert Rule**
2. Configurar reglas por tipo de error, frecuencia o tenant
3. Integrar con Slack, Email, PagerDuty, etc.

## Captura Manual de Errores

### Capturar Excepciones

```python
from sentry_sdk import capture_exception, capture_message

try:
    # Código que puede fallar
    procesar_encuesta(data)
except Exception as e:
    # Capturar excepción con contexto adicional
    capture_exception(e)
```

### Mensajes Personalizados

```python
from sentry_sdk import capture_message, set_context

# Mensaje informativo
capture_message("Usuario completó encuesta", level="info")

# Con contexto adicional
set_context("encuesta", {
    "id": survey.id,
    "preguntas": survey.questions.count(),
    "respuestas": survey.answers.count(),
})
capture_message("Encuesta procesada exitosamente", level="info")
```

### Breadcrumbs (Rastro de Acciones)

```python
from sentry_sdk import add_breadcrumb

# Registrar acciones del usuario antes de un error
add_breadcrumb(
    category="survey",
    message="Usuario seleccionó unidad",
    level="info",
    data={"unit_id": unit.id, "route": unit.route.name}
)

add_breadcrumb(
    category="survey",
    message="Usuario respondió pregunta",
    level="info",
    data={"question_id": question.id, "answer": answer}
)

# Si ocurre un error después, Sentry mostrará el rastro completo
```

## Mejores Prácticas

### 1. No Enviar Información Sensible

Aunque `send_default_pii=True` está habilitado, evitar enviar:
- Contraseñas
- Números de tarjetas de crédito
- Tokens de autenticación
- Datos personales sensibles (GDPR compliance)

```python
# Sanitizar datos antes de enviar
from sentry_sdk import set_context

set_context("user", {
    "id": user.id,
    "email": user.email[:3] + "***",  # Ofuscar email
    "role": user.role,
})
```

### 2. Usar Tags para Organización

```python
from sentry_sdk import set_tag

# Tags útiles para filtrado
set_tag("feature", "survey")
set_tag("tenant_schema", "cliente1")
set_tag("route_id", route.id)
set_tag("complaint_type", "driver_behavior")
```

### 3. Sampling Inteligente en Producción

Para reducir costos en Sentry, ajustar sampling rates:

```python
# En settings.py para producción
traces_sample_rate=0.2,  # 20% de transacciones
profiles_sample_rate=0.2,  # 20% de perfiles
```

### 4. Ignorar Errores Esperados

Configurar en Sentry dashboard para ignorar errores conocidos:
- **404 Not Found**: Usuarios accediendo a URLs inexistentes
- **Permission Denied**: Intentos de acceso no autorizado
- **CSRF Failed**: Tokens expirados (normal en sesiones largas)

### 5. Contexto de Tenant Siempre

Agregar el contexto de tenant en cada error para facilitar debugging:

```python
# En apps/organization/middleware.py (TenantActiveMiddleware)
from sentry_sdk import set_tag, set_context

class TenantActiveMiddleware:
    def process_request(self, request):
        if hasattr(request, 'tenant'):
            tenant = request.tenant
            set_tag("tenant_schema", tenant.schema_name)
            set_tag("tenant_name", tenant.name)
            set_context("tenant", {
                "id": str(tenant.id),
                "name": tenant.name,
                "schema": tenant.schema_name,
                "domain": request.get_host(),
            })
```

## Troubleshooting

### Sentry No Captura Errores

**Verificar que:**

1. La variable `SENTRY_DSN` está configurada:
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.SENTRY_DSN)
   ```

2. El DSN es válido y el proyecto existe en Sentry

3. Hay conexión a internet desde el servidor

4. Los errores no están siendo silenciados con `try/except` sin `capture_exception()`

### Exceso de Eventos

Si Sentry reporta límite de eventos alcanzado:

1. Reducir `traces_sample_rate` a 0.1 o 0.05
2. Ignorar errores comunes en Sentry dashboard
3. Usar filtros en `before_send`:

```python
def before_send(event, hint):
    # Ignorar ciertos errores
    if event.get('logger') == 'django.security.DisallowedHost':
        return None
    return event

sentry_sdk.init(
    dsn=SENTRY_DSN,
    before_send=before_send,
    ...
)
```

### Errores No Muestran Stack Trace Completo

Asegurarse de que `DEBUG=False` en producción para que Sentry capture el stack trace completo.

### Performance Lento Después de Instalar Sentry

Si hay impacto en rendimiento:

1. Reducir `traces_sample_rate` a 0.1 o menos
2. Deshabilitar profiling: `profiles_sample_rate=0`
3. Deshabilitar logs: `enable_logs=False`

## Recursos Adicionales

- [Documentación oficial de Sentry para Django](https://docs.sentry.io/platforms/python/guides/django/)
- [Best Practices para Sentry](https://docs.sentry.io/product/best-practices/)
- [Sentry Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Sentry Profiling](https://docs.sentry.io/product/profiling/)

## Soporte

Para problemas con la configuración de Sentry en este proyecto:

1. Revisar los logs de Django: `python manage.py runserver`
2. Verificar variables de entorno en `.env`
3. Consultar el dashboard de Sentry para errores de integración
4. Revisar la documentación oficial de Sentry
