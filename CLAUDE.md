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
- `statistical_summary/` - **TENANT_APPS**: Statistical dashboards and reports
- `qr_generator/` - **TENANT_APPS**: QR code generation for surveys/units

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

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic --no-input
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
- `SENTRY_DSN` - Sentry DSN for error tracking and performance monitoring (optional)
- `SENTRY_ENVIRONMENT` - Deployment environment (development, staging, production)

## Multi-tenant Workflow

1. **Create Organization**: From public admin (`/super-admin/`), create Organization with unique `schema_name`
2. **Add Domain**: Create Domain pointing to the organization (e.g., `cliente1.tuvozenruta.com`)
3. **Automatic Schema Creation**: Schema is auto-created due to `auto_create_schema = True` in Organization model
4. **Access Tenant**: Navigate to tenant domain to access tenant-specific admin and features

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

## Important Notes

- The `TenantMainMiddleware` must be first in MIDDLEWARE
- Database engine must be `django_tenants.postgresql_backend`
- When working with models, check if they belong to SHARED_APPS or TENANT_APPS
- Always specify `--schema` flag when creating superusers or running tenant-specific commands
- Never run destructive git operations or bypass hooks without explicit request
