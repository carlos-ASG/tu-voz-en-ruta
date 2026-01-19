---
name: django-health
description: >
  Django health check configuration and patterns using django-health-check for system monitoring, Docker healthchecks, and Kubernetes probes.
  Trigger: When implementing health checks, monitoring endpoints, or readiness/liveness probes in Django.
license: Apache-2.0
metadata:
  author: Carlos
  version: "1.0"
  scope: [root]
  auto_invoke: "Implementing health checks/monitoring endpoints"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
---

## What is django-health-check?

`django-health-check` is a pluggable app that provides health check endpoints for Django applications. It's essential for:

- **Container orchestration**: Docker Compose, Kubernetes liveness/readiness probes
- **Load balancers**: Health-based routing decisions
- **Monitoring systems**: Uptime tracking, alerting
- **Multi-tenant apps**: Database and migrations status per tenant

**Key Benefits:**

- Built-in checks: database, cache, storage, migrations
- Custom check support
- JSON/HTML output formats
- Pluggable architecture
- Works in public schema (no tenant required)

---

## Installation

```bash
pip install django-health-check
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "health_check",
    "health_check.db",                 # Database connectivity
    "health_check.contrib.migrations", # Pending migrations check
    # Optional checks:
    # "health_check.cache",            # Cache backend
    # "health_check.storage",          # File storage
    # "health_check.contrib.celery",   # Celery workers
    # "health_check.contrib.redis",    # Redis
]
```

---

## URL Configuration (REQUIRED)

**Important**: Health checks should be accessible in the **public schema** (without tenant) for Docker/Kubernetes to reach them easily.

```python
# urls_public.py (Public URLs - no tenant required)
from django.urls import path, include

urlpatterns = [
    path("health/", include("health_check.urls")),
    # Other public URLs...
]
```

```python
# settings.py
PUBLIC_SCHEMA_URLCONF = "buzon_quejas.urls_public"  # Health checks here
ROOT_URLCONF = "buzon_quejas.urls_tenant"            # Tenant-specific URLs
```

---

## Available Endpoints

```bash
# Check all health endpoints
curl http://localhost:8000/health/

# Get JSON response
curl http://localhost:8000/health/?format=json

# Check specific component
curl http://localhost:8000/health/db/
curl http://localhost:8000/health/migrations/
curl http://localhost:8000/health/cache/
```

**Response Example (JSON):**

```json
{
  "db": "working",
  "migrations": "working"
}
```

**HTTP Status Codes:**

- `200 OK`: All checks passed
- `500 Internal Server Error`: One or more checks failed

---

## Built-in Checks

### Database Check

```python
# Enabled by: "health_check.db" in INSTALLED_APPS
# Checks: Can connect to database and execute queries
# URL: /health/db/
```

### Migrations Check

```python
# Enabled by: "health_check.contrib.migrations" in INSTALLED_APPS
# Checks: No pending migrations
# URL: /health/migrations/
```

### Cache Check

```python
# Enabled by: "health_check.cache" in INSTALLED_APPS
# Checks: Can read/write to cache backend
# URL: /health/cache/
```

---

## Docker Healthcheck (REQUIRED)

```dockerfile
# Dockerfile
FROM python:3.11-slim

# ... other setup ...

# Health check for Docker
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1
```

```yaml
# docker-compose.yml
services:
  web:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
```

---

## Kubernetes Probes (REQUIRED)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
spec:
  template:
    spec:
      containers:
      - name: web
        image: myapp:latest
        
        # Liveness probe: Restart if unhealthy
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
            httpHeaders:
            - name: Host
              value: localhost
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Readiness probe: Remove from service if not ready
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
            httpHeaders:
            - name: Host
              value: localhost
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

**Probe Differences:**

| Probe | Purpose | Failure Action |
|-------|---------|----------------|
| **Liveness** | Is app alive? | Restart container |
| **Readiness** | Is app ready? | Remove from service (no traffic) |
| **Startup** | Has app started? | Wait before other probes |

---

## Custom Health Checks

```python
# myapp/health_checks.py
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable

class TenantCountCheck(BaseHealthCheckBackend):
    """Check if at least one tenant exists."""
    
    critical_service = False  # True = fail entire health check if this fails
    
    def check_status(self):
        from apps.organization.models import Organization
        
        try:
            tenant_count = Organization.objects.count()
            if tenant_count == 0:
                self.add_error(ServiceUnavailable("No tenants configured"))
        except Exception as e:
            self.add_error(ServiceUnavailable(f"Error checking tenants: {e}"))
    
    def identifier(self):
        return "tenant_count"

# Register custom check
# settings.py
INSTALLED_APPS = [
    # ...
    "myapp",  # Contains health_checks.py
]

# myapp/apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = "myapp"
    
    def ready(self):
        from health_check.plugins import plugin_dir
        from .health_checks import TenantCountCheck
        plugin_dir.register(TenantCountCheck)
```

---

## Multi-tenant Considerations

For `django-tenants` apps:

**✅ DO:**

- Configure health checks in **public schema** (`PUBLIC_SCHEMA_URLCONF`)
- Use database checks to verify PostgreSQL connectivity
- Use migrations check to verify schema sync

**❌ DON'T:**

- Put health checks behind tenant middleware (Docker/K8s can't provide tenant domain)
- Check tenant-specific data in health checks (use separate monitoring for that)

---

## Monitoring Integration

### Uptime Monitoring (UptimeRobot, Pingdom, etc.)

```
Monitor URL: https://tuvozenruta.com/health/
Check interval: 1-5 minutes
Expected status: 200 OK
Alert on: 500 errors or timeout
```

### Prometheus + Grafana

```python
# For Prometheus metrics, use django-prometheus instead:
# pip install django-prometheus

# settings.py
INSTALLED_APPS = [
    "django_prometheus",
    # ...
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    # ... other middleware ...
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

# urls_public.py
urlpatterns = [
    path("metrics/", include("django_prometheus.urls")),
    path("health/", include("health_check.urls")),
]
```

---

## Common Commands

```bash
# Test health endpoint locally
curl http://localhost:8000/health/

# Test with JSON format
curl http://localhost:8000/health/?format=json

# Test specific check
curl http://localhost:8000/health/db/

# Test from Docker container
docker compose exec web curl -f http://localhost:8000/health/

# View health check in browser (HTML output)
open http://localhost:8000/health/
```

---

## Best Practices Checklist

**ALWAYS:**

- ✅ Configure health checks in public schema (no tenant required)
- ✅ Use database check to verify PostgreSQL connectivity
- ✅ Use migrations check to catch schema drift
- ✅ Add Docker HEALTHCHECK in Dockerfile
- ✅ Configure Kubernetes liveness + readiness probes
- ✅ Set reasonable timeouts (3s is good default)
- ✅ Test health endpoints work without authentication
- ✅ Return JSON format for programmatic checks
- ✅ Use `critical_service=False` for non-essential custom checks
- ✅ Monitor health endpoint with external service

**NEVER:**

- ❌ Put health checks behind tenant middleware
- ❌ Require authentication for health endpoints
- ❌ Make health checks do expensive operations
- ❌ Use same probe settings for liveness and readiness
- ❌ Set initialDelaySeconds too low (app needs time to start)
- ❌ Forget to install `curl` in Docker image for healthcheck

---

## Troubleshooting

### Health check returns 500

```bash
# Check logs for specific error
docker compose logs web | grep health

# Test each check individually
curl http://localhost:8000/health/db/
curl http://localhost:8000/health/migrations/
```

### Docker healthcheck failing

```bash
# Check if curl is installed in container
docker compose exec web which curl

# Check if port 8000 is listening
docker compose exec web netstat -tlnp | grep 8000

# Manually run healthcheck command
docker compose exec web curl -f http://localhost:8000/health/
```

### Kubernetes probe failing

```bash
# Check pod logs
kubectl logs <pod-name>

# Check probe configuration
kubectl describe pod <pod-name>

# Manually test from pod
kubectl exec -it <pod-name> -- curl http://localhost:8000/health/
```

---

## Resources

- **Documentation**: https://github.com/revsys/django-health-check
- **Docker healthcheck**: https://docs.docker.com/engine/reference/builder/#healthcheck
- **Kubernetes probes**: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
