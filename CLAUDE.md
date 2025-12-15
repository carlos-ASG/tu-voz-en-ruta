# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-tenant Django application for public transport complaint and survey management ("Tu Voz en Ruta"). The system uses `django-tenants` to provide isolated database schemas per organization, allowing multiple transport organizations to operate independently on the same infrastructure.

## Architecture

**Multi-tenancy Structure:**
- Uses `django-tenants` with PostgreSQL schemas for tenant isolation
- Each organization (transport company) gets its own schema with isolated data
- Public schema (`schema_name='public'`) contains shared data (Organization, Domain models)
- Tenant schemas contain organization-specific data (surveys, complaints, routes, units)

**Schema Routing:**
- `PUBLIC_SCHEMA_URLCONF = 'buzon_quejas.urls_public'` - Public tenant URLs (super-admin, organization selection)
- `ROOT_URLCONF = 'buzon_quejas.urls_tenant'` - Tenant-specific URLs (admin, interviews, statistics, QR generator)
- Public admin accessible at `/super-admin/`
- Tenant admin accessible at `/admin/` (different admin site per tenant)

**Django Apps:**

- `organization/` - **SHARED_APPS**: Multi-tenant models (Organization, Domain), organization selection views
- `interview/` - **TENANT_APPS**: Survey/complaint system with Question, Answer, SurveySubmission, Complaint models (split across multiple files in models/)
- `transport/` - **TENANT_APPS**: Route and Unit (vehicle) models, custom tenant admin site
- `statistical_summary/` - **TENANT_APPS**: Statistical dashboards, reports, and aggregated statistics generation
- `qr_generator/` - **TENANT_APPS**: QR code generation for surveys/units
- `users/` - **TENANT_APPS**: Custom user management per tenant

**Database Models:**
- Organization models are in `organization/models.py` (single file)
- Interview models are split into separate files in `interview/models/` directory (imported via `__init__.py`)
- Each app uses UUID primary keys for Organization

## Common Commands

**Database Setup (First Time):**
```bash
# Start PostgreSQL with Docker
docker compose up -d

# Initialize database with shared schema and public tenant
python start_db.py

# Create superuser for public schema
python manage.py createsuperuser --schema=public

# Populate database with test data
python populate_db.py
```

**Migrations:**
```bash
# Create migrations (shared schema)
python manage.py makemigrations

# Apply shared schema migrations only
python manage.py migrate_schemas --shared

# Apply migrations to all tenant schemas
python manage.py migrate_schemas

# Apply migrations to specific tenant
python manage.py migrate_schemas --schema=<schema_name>

# Dry-run check for migration issues
python manage.py makemigrations --dry-run --check
```

**Development Server:**
```bash
# Run development server (default port 8000)
python manage.py runserver

# Access public admin: http://localhost:8000/super-admin/
# Access tenant admin: http://<subdomain>.localhost:8000/admin/
```

**Validation and Tests:**
```bash
# Django system checks
python manage.py check

# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.interview

# Run specific test class
python manage.py test apps.interview.tests.TestSurveyForm

# Collect static files
python manage.py collectstatic --no-input
```

**Management Commands:**
```bash
# Generate aggregated reports (statistical_summary app)
python manage.py generar_reportes_agregados

# Check health status
curl http://localhost:8000/health/
```

**Production Build (Railway/Render):**
```bash
# Build script (see build.sh)
./build.sh
```

## Environment Variables

Required variables (see `.env-example`):
- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://buzon_user:buzon_password@localhost:5432/buzon_db`)
- `SECRET_KEY` - Django secret key
- `RECAPTCHA_PUBLIC_KEY` - Google reCAPTCHA public key
- `RECAPTCHA_PRIVATE_KEY` - Google reCAPTCHA private key
- `REDIS_URL` - Redis connection for rate limiting (default: `redis://localhost:6379/0`)
- `SENTRY_DSN` - Sentry DSN for error tracking and performance monitoring (optional)
- `SENTRY_ENVIRONMENT` - Deployment environment (development, staging, production)
- `DEBUG` - Enable debug mode (default: `False`, set to `True` for development)

## Multi-tenant Workflow

1. **Create Organization**: From public admin (`/super-admin/`), create Organization with unique `schema_name`
2. **Add Domain**: Create Domain pointing to the organization (e.g., `cliente1.tuvozenruta.com`)
3. **Automatic Schema Creation**: Schema is auto-created due to `auto_create_schema = True` in Organization model
4. **Access Tenant**: Navigate to tenant domain to access tenant-specific admin and features

## Survey Form Access

**URL Pattern:**

Each unit has its own dedicated survey form URL:

```text
/survey/<transit_number>/
```

**Example:**

```text
https://cliente1.tuvozenruta.com/survey/ABC123/
```

**Key Features:**

- Each unit is accessed via its unique `transit_number` in the URL path
- Designed for QR code integration - each QR contains the unit-specific URL
- General unit selector available at `/survey/` (from admin panel or organization selection)
- Auto-redirects to first unit if only one exists, or shows selector for multiple units
- Returns 404 if the unit doesn't exist

**URL Structure:**

- Unit selection: `/survey/` (auto-redirects if only 1 unit, or shows selector)
- Survey form: `/survey/<transit_number>/`
- Form submission: `/survey/<transit_number>/submit/`
- Thank you page: `/survey/thank-you/`

**Implementation:**

- URLs: [apps/interview/urls.py](apps/interview/urls.py)
- Unit selector view: [apps/interview/views.py:13](apps/interview/views.py#L13) - `select_unit_for_survey()`
- Survey form view: [apps/interview/views.py:73](apps/interview/views.py#L73) - `survey_form(transit_number)`
- Submit view: [apps/interview/views.py:107](apps/interview/views.py#L107) - `submit_survey(transit_number)`
- Templates:
  - [apps/interview/templates/interview/select_unit.html](apps/interview/templates/interview/select_unit.html) - Unit selector
  - [apps/interview/templates/interview/no_units.html](apps/interview/templates/interview/no_units.html) - No units available
  - [apps/interview/templates/interview/form_section.html](apps/interview/templates/interview/form_section.html) - Survey form
- Form: [apps/interview/forms/select_unit_form.py](apps/interview/forms/select_unit_form.py) - `SelectUnitForm`

**Form Structure:**

1. **Section 1**: Unit information display (read-only, shows transit_number, route, internal_number)
2. **Section 2**: Dynamic survey questions (ratings, text, choice, multi-choice)
3. **Section 3**: Optional complaint with reason and text
4. **reCAPTCHA**: Spam protection

## Key Conventions (from AGENTS.md)

- **Language**: Comments and documentation in Spanish
- **Commit Messages**: Spanish, imperative tense, atomic commits
- **Code Style**: PEP8 for Python
- **Security**: Validate all user inputs, use Django's built-in protections (CSRF, XSS, SQL injection)
- **Tests**: Include tests for functional changes
- **Migrations**: Always include migrations when modifying models, explain their purpose
- **Branch Naming**: Use `feature/`, `fix/`, `chore/` prefixes
- **No Secrets**: Never commit credentials; use environment variables

## Database Reference

Database dump location: `#file:database.sql` (mentioned in AGENTS.md)

## Deployment

- **Platform**: Railway/Render (configured via `Procfile`)
- **Procfile**: Runs `collectstatic`, `start_db.py`, then `gunicorn`
- **Static Files**: Managed by WhiteNoise in production
- **Time Zone**: America/Mazatlan (UTC-7, Nayarit, México)
- **Allowed Hosts**: `tuvozenruta.com`, `*.tuvozenruta.com`, `*.up.railway.app`

## Admin Customization

Uses `django-jazzmin` for enhanced admin interface with custom branding, icons, and navigation (configured extensively in `settings.py:196-337`).

## Monitoring

**Error Tracking & Performance:**

- Uses **Sentry** for error tracking, performance monitoring, and profiling
- Configuration in [settings.py:28-54](buzon_quejas/settings.py#L28-L54)
- Full documentation: [MONITORING.md](MONITORING.md)

**Key Features:**

- Automatic error capture (exceptions, 500 errors, database errors)
- Performance monitoring with transaction tracing
- CPU and memory profiling
- Multi-tenant context tagging (identify errors by tenant/organization)
- Log integration

**Quick Setup:**

```bash
# Add to .env
SENTRY_DSN=https://your-key@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

**Multi-tenant Context:**

To identify which tenant generated an error, add Sentry tags in middleware:

```python
from sentry_sdk import set_tag, set_context

set_tag("tenant_schema", request.tenant.schema_name)
set_context("tenant", {"name": request.tenant.name})
```

See [MONITORING.md](MONITORING.md) for complete configuration, best practices, and troubleshooting.

## Health Checks

**System Health Monitoring:**

- Uses **django-health-check** to provide health check endpoints
- Configured in public schema (accessible without tenant)
- Full documentation: [HEALTH_CHECKS.md](HEALTH_CHECKS.md)

**Available Checks:**

- Database connectivity (`health_check.db`)
- Pending migrations (`health_check.contrib.migrations`)

**Endpoints:**

```bash
# Check all health endpoints
curl http://localhost:8000/health/

# Get JSON response
curl http://localhost:8000/health/?format=json

# Check specific component
curl http://localhost:8000/health/db/
curl http://localhost:8000/health/migrations/
```

See [HEALTH_CHECKS.md](HEALTH_CHECKS.md) for Docker healthchecks, Kubernetes probes, and monitoring integration.

## Rate Limiting

**Survey Submission Protection:**

- Uses **django-ratelimit** with Redis backend
- Configured in [interview/views.py:107](apps/interview/views.py#L107) - `submit_survey()` function
- Rate limit: 1 submission per IP+Unit combination every 15 minutes
- Custom key function: `get_ratelimit_key_ip_and_unit` combines IP and unit ID

**Configuration:**

```python
@ratelimit(key=get_ratelimit_key_ip_and_unit, rate='1/15m', method='POST', block=False)
def submit_survey(request):
    if getattr(request, 'limited', False):
        # Handle rate limit exceeded
```

**Required Environment Variable:**

```bash
# Redis connection for rate limiting
REDIS_URL=redis://localhost:6379/0
```

## Important Notes

- The `TenantMainMiddleware` must be first in MIDDLEWARE
- Database engine must be `django_tenants.postgresql_backend`
- When working with models, check if they belong to SHARED_APPS or TENANT_APPS
- Always specify `--schema` flag when creating superusers or running tenant-specific commands
- Never run destructive git operations or bypass hooks without explicit request
