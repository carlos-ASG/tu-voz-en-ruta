# Health Checks (Verificación de Estado)

## Introducción

Este proyecto utiliza `django-health-check` para proporcionar endpoints de verificación de estado que permiten monitorear la salud de la aplicación y sus dependencias. Los health checks son esenciales para:

- **Monitoreo continuo**: Detectar problemas antes de que afecten a los usuarios
- **Orquestación**: Kubernetes, Docker Swarm y otros orquestadores usan health checks para gestionar contenedores
- **Balanceadores de carga**: Determinar si una instancia debe recibir tráfico
- **Alertas automáticas**: Integración con sistemas de monitoreo (Prometheus, Datadog, etc.)
- **Debugging**: Identificar rápidamente qué componente está fallando

## Configuración Actual

### Apps Instaladas

Los siguientes módulos de health check están configurados en `settings.py` como parte de `SHARED_APPS`:

```python
'health_check',                      # Core - funcionalidad base
'health_check.db',                   # Verificación de base de datos
'health_check.contrib.migrations',   # Verificación de migraciones pendientes
```

> **Nota**: La verificación de almacenamiento (`health_check.storage`) no está configurada ya que este proyecto no utiliza el sistema de almacenamiento por defecto de Django.

### URL Configurada

Los health checks están disponibles en el **esquema público** (no requieren tenant específico):

```python
# buzon_quejas/urls_public.py
path('health/', include('health_check.urls')),
```

## Uso de los Endpoints

### Endpoint Principal

**URL**: `http://localhost:8000/health/`

Este endpoint ejecuta **todas** las verificaciones configuradas y devuelve:
- **HTTP 200**: Si todas las verificaciones pasan
- **HTTP 500**: Si alguna verificación falla

**Ejemplo de respuesta exitosa**:
```
DatabaseBackend             ... working
MigrationsHealthCheck       ... working
```

**Ejemplo con fallo**:
```
DatabaseBackend             ... unavailable: could not connect to server
MigrationsHealthCheck       ... working
```

### Verificaciones Individuales

Puedes verificar componentes específicos usando estos endpoints:

| Endpoint | Descripción |
|----------|-------------|
| `/health/` | Todas las verificaciones |
| `/health/?format=json` | Resultado en formato JSON |
| `/health/db/` | Solo verificación de base de datos |
| `/health/migrations/` | Solo verificación de migraciones |

### Formato JSON

Para obtener respuestas en JSON (útil para integraciones), agrega `?format=json`:

```bash
curl http://localhost:8000/health/?format=json
```

**Respuesta JSON de ejemplo**:
```json
{
  "DatabaseBackend": "working",
  "MigrationsHealthCheck": "working"
}
```

## Ejemplos de Uso

### 1. Verificación Manual en Desarrollo

```bash
# Verificación completa
curl http://localhost:8000/health/

# Verificación en formato JSON
curl http://localhost:8000/health/?format=json

# Solo base de datos
curl http://localhost:8000/health/db/
```

### 2. Script de Monitoreo

```bash
#!/bin/bash
# check_health.sh

HEALTH_URL="http://localhost:8000/health/"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $STATUS -eq 200 ]; then
    echo "✓ Sistema saludable"
    exit 0
else
    echo "✗ Sistema con problemas (HTTP $STATUS)"
    curl $HEALTH_URL
    exit 1
fi
```

### 3. Docker Healthcheck

Si usas Docker, agrega un healthcheck en tu `Dockerfile`:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1
```

O en `docker-compose.yml`:

```yaml
services:
  web:
    image: tuvozenruta:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 4. Kubernetes Liveness/Readiness Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tuvozenruta
spec:
  containers:
  - name: app
    image: tuvozenruta:latest
    livenessProbe:
      httpGet:
        path: /health/
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health/
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
```

## Verificaciones Disponibles

### Base de Datos (`health_check.db`)

Verifica que:
- La conexión a PostgreSQL está activa
- Se pueden ejecutar queries básicas
- El esquema público es accesible

**Posibles problemas**:
- Credenciales incorrectas
- PostgreSQL no está ejecutándose
- Red bloqueada/firewall
- Límite de conexiones alcanzado

### Migraciones (`health_check.contrib.migrations`)

Verifica que:
- No hay migraciones pendientes
- La base de datos está actualizada

**Posibles problemas**:
- Se agregaron migraciones pero no se ejecutaron
- Alguien hizo cambios en modelos sin crear migración

## Plugins Adicionales Disponibles

Puedes instalar y configurar plugins adicionales según tus necesidades:

### Cache (`health_check.cache`)

```bash
pip install django-health-check[cache]
```

```python
# settings.py - SHARED_APPS
'health_check.cache',
```

Verifica: Redis, Memcached u otro backend de cache configurado.

### Celery (`health_check.contrib.celery`)

```bash
pip install django-health-check[celery]
```

```python
# settings.py - SHARED_APPS
'health_check.contrib.celery',
```

Verifica: Workers de Celery están activos y respondiendo.

### RabbitMQ (`health_check.contrib.rabbitmq`)

```bash
pip install django-health-check[rabbitmq]
```

```python
# settings.py - SHARED_APPS
'health_check.contrib.rabbitmq',
```

Verifica: RabbitMQ está disponible y aceptando conexiones.

### S3 Storage (`health_check.contrib.s3boto3_storage`)

```bash
pip install django-health-check[s3boto3]
```

```python
# settings.py - SHARED_APPS
'health_check.contrib.s3boto3_storage',
```

Verifica: Acceso a buckets de S3 (útil si usas S3 para archivos estáticos/media).

### psutil (Recursos del Sistema)

```bash
pip install django-health-check[psutil]
```

```python
# settings.py - SHARED_APPS
'health_check.contrib.psutil',

# Configuración opcional
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # Alerta si el disco está >90% lleno
    'MEMORY_MIN': 100,     # Alerta si quedan <100MB de RAM
}
```

Verifica: Uso de disco, memoria, CPU.

## Configuración Avanzada

### Personalizar Configuración

Agrega en `settings.py`:

```python
HEALTH_CHECK = {
    # Cachear resultados por 60 segundos para evitar sobrecarga
    'CACHE_TIMEOUT': 60,

    # Mostrar mensajes de error detallados (solo en desarrollo)
    'ERRORS_VERBOSE': DEBUG,

    # Plugins a ejecutar (por defecto: todos los instalados)
    'PLUGINS': [
        'health_check.db.backends.DatabaseBackend',
        'health_check.contrib.migrations.backends.MigrationsHealthCheck',
    ],
}
```

### Crear Verificación Personalizada

Crea un archivo `apps/organization/health_checks.py`:

```python
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

class TenantHealthCheck(BaseHealthCheckBackend):
    """Verifica que al menos un tenant esté activo"""

    critical_service = True  # Si falla, marca el sistema como no saludable

    def check_status(self):
        from apps.organization.models import Organization

        active_tenants = Organization.objects.filter(is_active=True).count()

        if active_tenants == 0:
            raise ServiceUnavailable("No hay tenants activos")

        self.add_message(f"{active_tenants} tenant(s) activo(s)")

    def identifier(self):
        return "Tenants Activos"
```

Registra en `apps/organization/apps.py`:

```python
from django.apps import AppConfig
from health_check.plugins import plugin_dir

class OrganizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.organization'

    def ready(self):
        from .health_checks import TenantHealthCheck
        plugin_dir.register(TenantHealthCheck)
```

## Integración con Servicios de Monitoreo

### UptimeRobot

1. Crear nuevo monitor HTTP(S)
2. URL: `https://tuvozenruta.com/health/`
3. Intervalo: 5 minutos
4. Keyword: "working" (espera encontrar esta palabra)

### Prometheus + Blackbox Exporter

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://tuvozenruta.com/health/
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

### Datadog

```python
# settings.py
HEALTH_CHECK = {
    'DATADOG': {
        'API_KEY': os.getenv('DATADOG_API_KEY'),
        'APP_KEY': os.getenv('DATADOG_APP_KEY'),
    }
}
```

### Sentry

Los errores de health check se reportarán automáticamente a Sentry si está configurado.

## Consideraciones de Seguridad

### 1. Proteger en Producción

Los health checks pueden exponer información sensible. Considera:

```python
# settings.py
HEALTH_CHECK = {
    # Requerir autenticación para endpoints de health
    'REQUIRE_AUTHENTICATION': not DEBUG,

    # No mostrar detalles de error en producción
    'ERRORS_VERBOSE': DEBUG,
}
```

### 2. Rate Limiting

Protege contra abuso:

```python
# Usar django-ratelimit
from ratelimit.decorators import ratelimit

# En urls.py, puedes envolver las vistas
from django.urls import path
from health_check.views import MainView

urlpatterns = [
    path('health/', ratelimit(key='ip', rate='10/m')(MainView.as_view())),
]
```

### 3. Restricción por IP

```python
# En production, limita acceso solo desde red interna
HEALTH_CHECK = {
    'ALLOWED_IPS': ['10.0.0.0/8', '172.16.0.0/12'],  # Solo IPs privadas
}
```

## Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'health_check'"

**Solución**:
```bash
source venv/bin/activate
pip install django-health-check
```

### Problema: "django.db.migrations.exceptions.InconsistentMigrationHistory"

**Solución**:
```bash
# Aplicar migraciones al esquema público
python manage.py migrate_schemas --shared
```

### Problema: Health check siempre devuelve 500

**Solución**:
1. Verifica los logs: `python manage.py runserver`
2. Prueba cada plugin individualmente: `/health/db/`, `/health/storage/`
3. Revisa la configuración de `DATABASES` y `STATIC_ROOT`

### Problema: "MigrationsHealthCheck ... unavailable"

**Solución**:
```bash
# Verificar migraciones pendientes
python manage.py showmigrations

# Aplicar migraciones
python manage.py migrate_schemas
```

### Problema: En producción no funciona

**Solución**:
1. Verifica que `ALLOWED_HOSTS` incluye tu dominio
2. Asegúrate de que el health check está en `urls_public.py` (no en `urls_tenant.py`)
3. Verifica que `health_check` está en `SHARED_APPS`

## Testing en CI/CD

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run migrations
        run: |
          python manage.py migrate_schemas --shared

      - name: Health Check
        run: |
          python manage.py runserver &
          sleep 5
          curl -f http://localhost:8000/health/ || exit 1
```

## Recursos Adicionales

- **Documentación oficial**: https://django-health-check.readthedocs.io/
- **Repositorio GitHub**: https://github.com/revsys/django-health-check
- **Django Tenants**: https://django-tenants.readthedocs.io/

## Comandos Útiles

```bash
# Verificar estado localmente
curl http://localhost:8000/health/

# Verificar en producción
curl https://tuvozenruta.com/health/

# Verificar con detalles JSON
curl https://tuvozenruta.com/health/?format=json | jq .

# Solo código de estado HTTP
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/

# Con timeout
curl --max-time 10 http://localhost:8000/health/
```

## Próximos Pasos Recomendados

1. **Aplicar migraciones**: `python manage.py migrate_schemas --shared`
2. **Probar localmente**: Visita `http://localhost:8000/health/`
3. **Configurar monitoreo**: Integra con UptimeRobot o similar
4. **Agregar alertas**: Configura notificaciones cuando fallen health checks
5. **Documentar en Runbook**: Incluye procedimientos de respuesta ante fallos
6. **Configurar CI/CD**: Agrega health checks a tu pipeline de deployment
