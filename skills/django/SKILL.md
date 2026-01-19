---
name: django
description: >
  Django modern patterns and best practices for views, forms, URL routing, and management commands.
  Trigger: When implementing or refactoring Django views, forms, URLs, or commands.
license: Apache-2.0
metadata:
  author: Carlos
  version: "1.0"
  scope: [root]
  auto_invoke:
    - "Writing Django views/forms/URLs"
    - "Implementing survey form views"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
---

## Django Forms with Type Hints (REQUIRED)

```python
from django import forms
from django.core.exceptions import ValidationError
from typing import Any

class UserForm(forms.ModelForm):
    """Type-safe ModelForm with validation."""

    class Meta:
        model = User
        fields = ["name", "email", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {"name": "Full Name"}
        help_texts = {"email": "We'll never share your email."}

    def clean_email(self) -> str:
        """Validate email field."""
        email = self.cleaned_data.get("email", "")
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Email already exists")
        return email.lower()

    def clean(self) -> dict[str, Any]:
        """Cross-field validation."""
        cleaned_data = super().clean()
        # Add cross-field validation logic here
        return cleaned_data

# Common field types
class AdvancedForm(forms.Form):
    text = forms.CharField(max_length=100)
    textarea = forms.CharField(widget=forms.Textarea)
    integer = forms.IntegerField(min_value=0, max_value=100)
    choice = forms.ChoiceField(choices=[("opt1", "Option 1")])
    multiple_choice = forms.MultipleChoiceField(choices=[("opt1", "Option 1")])
    boolean = forms.BooleanField(required=False)
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    file = forms.FileField()
    email = forms.EmailField()
```

## Function-Based Views (REQUIRED)

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

def user_list(request: HttpRequest) -> HttpResponse:
    """List all active users."""
    users = User.objects.filter(status="active")
    return render(request, "users/list.html", {"users": users})

def user_create(request: HttpRequest) -> HttpResponse:
    """Create new user."""
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.name} created!")
            return redirect("user_detail", user_id=user.id)
    else:
        form = UserForm()
    return render(request, "users/create.html", {"form": form})

def user_update(request: HttpRequest, user_id: int) -> HttpResponse:
    """Update existing user."""
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated!")
            return redirect("user_detail", user_id=user.id)
    else:
        form = UserForm(instance=user)
    return render(request, "users/update.html", {"form": form, "user": user})
```

## Class-Based Views (REQUIRED)

```python
from django.views.generic import ListView, CreateView, UpdateView, TemplateView, FormView
from django.urls import reverse_lazy
from typing import Any

class HomeView(TemplateView):
    """Simple template view."""
    template_name = "home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["total_users"] = User.objects.count()
        return context

class UserCreateView(CreateView):
    """Create view with ModelForm."""
    model = User
    form_class = UserForm
    template_name = "users/create.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        messages.success(self.request, "User created!")
        return super().form_valid(form)

class ContactFormView(FormView):
    """Form view without model."""
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, "Message sent!")
        return super().form_valid(form)
```

## URL Routing with django-tenants (REQUIRED)

```python
# urls_public.py (Public URLs - no tenant required)
"""Public URLs: landing, auth, tenant creation"""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("create-tenant/", views.create_tenant, name="create_tenant"),
]
```

```python
# urls_tenant.py (Tenant URLs - require tenant context)
"""Tenant-specific URLs with access to request.tenant"""
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("users/", include([
        path("", views.user_list, name="user_list"),
        path("<int:user_id>/", views.user_detail, name="user_detail"),
        path("create/", views.user_create, name="user_create"),
        path("<int:user_id>/update/", views.user_update, name="user_update"),
    ])),
]
```

```python
# App-level URLs (users/urls.py)
from django.urls import path
from . import views

app_name = "users"  # Namespace for reverse lookups

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path("<int:user_id>/", views.user_detail, name="user_detail"),
    path("create/", views.user_create, name="user_create"),
]
```

```python
# Tenant-aware views
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.db import connection

def dashboard(request: HttpRequest) -> HttpResponse:
    """Tenant-specific dashboard."""
    tenant = request.tenant  # or connection.tenant
    context = {
        "tenant_name": tenant.name,
        "users_count": User.objects.count(),  # Tenant-specific
    }
    return render(request, "dashboard.html", context)

# Reversing URLs
from django.urls import reverse
url = reverse("user_detail", kwargs={"user_id": 123})  # /users/123/
url = reverse("users:user_detail", kwargs={"user_id": 123})  # With namespace
```

```python
# settings.py configuration
TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"
PUBLIC_SCHEMA_URLCONF = "myproject.urls_public"  # Public URLs
ROOT_URLCONF = "myproject.urls_tenant"  # Tenant URLs
```

## Management Commands (REQUIRED)

```python
# users/management/commands/create_test_users.py
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context
from typing import Any

class Command(BaseCommand):
    help = "Create test users for development"

    def add_arguments(self, parser) -> None:
        parser.add_argument("count", type=int, help="Number of users")
        parser.add_argument("--status", type=str, default="active")
        parser.add_argument("--schema", type=str, help="Tenant schema")

    def handle(self, *args: Any, **options: Any) -> None:
        count = options["count"]
        status = options["status"]
        schema = options.get("schema")

        # Tenant-specific operation
        if schema:
            with schema_context(schema):
                self._create_users(count, status)
        else:
            self._create_users(count, status)

    def _create_users(self, count: int, status: str) -> None:
        try:
            for i in range(count):
                User.objects.create(
                    name=f"Test User {i+1}",
                    email=f"test{i+1}@example.com",
                    status=status
                )
            self.stdout.write(
                self.style.SUCCESS(f"Created {count} users")
            )
        except Exception as e:
            raise CommandError(f"Error: {e}")

# Usage:
# python manage.py create_test_users 10
# python manage.py create_test_users 5 --schema=tenant1
```

## Basic Django Commands

```bash
# Development
python manage.py runserver
python manage.py collectstatic
python manage.py check
python manage.py check --deploy

# Custom commands
python manage.py <command_name>
python manage.py help <command_name>
```

## Survey Form Access Pattern (Project-Specific)

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

```python
# apps/interview/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Unit selection (redirects if 1 unit, shows selector if multiple)
    path("survey/", views.select_unit_for_survey, name="select_unit_for_survey"),
    
    # Survey form for specific unit
    path("survey/<str:transit_number>/", views.survey_form, name="survey_form"),
    
    # Form submission
    path("survey/<str:transit_number>/submit/", views.submit_survey, name="submit_survey"),
    
    # Thank you page
    path("survey/thank-you/", views.survey_thank_you, name="survey_thank_you"),
]
```

**Implementation:**

```python
# apps/interview/views.py
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from apps.transport.models import Unit

def select_unit_for_survey(request: HttpRequest) -> HttpResponse:
    """
    Unit selector for survey.
    - If only 1 unit: auto-redirect to survey form
    - If multiple units: show selector
    - If no units: show error page
    """
    units = Unit.objects.all()
    count = units.count()
    
    if count == 0:
        return render(request, "interview/no_units.html")
    elif count == 1:
        # Auto-redirect to survey form
        unit = units.first()
        return redirect("survey_form", transit_number=unit.transit_number)
    else:
        # Show unit selector
        return render(request, "interview/select_unit.html", {"units": units})

def survey_form(request: HttpRequest, transit_number: str) -> HttpResponse:
    """Display survey form for specific unit."""
    unit = get_object_or_404(Unit, transit_number=transit_number)
    questions = Question.objects.filter(is_active=True).order_by("order")
    
    return render(request, "interview/form_section.html", {
        "unit": unit,
        "questions": questions,
    })

def submit_survey(request: HttpRequest, transit_number: str) -> HttpResponse:
    """Process survey submission."""
    if request.method != "POST":
        return redirect("survey_form", transit_number=transit_number)
    
    unit = get_object_or_404(Unit, transit_number=transit_number)
    
    # Process form (with rate limiting - see django-ratelimit skill)
    # ...
    
    return redirect("survey_thank_you")
```

**Form Structure:**

1. **Section 1**: Unit information display (read-only, shows transit_number, route, internal_number)
2. **Section 2**: Dynamic survey questions (ratings, text, choice, multi-choice)
3. **Section 3**: Optional complaint with reason and text
4. **reCAPTCHA**: Spam protection

---

## Admin Customization with django-jazzmin

**Installation:**

```bash
pip install django-jazzmin
```

**Configuration:**

```python
# settings.py
INSTALLED_APPS = [
    "jazzmin",  # Must be before django.contrib.admin
    "django.contrib.admin",
    # ...
]

JAZZMIN_SETTINGS = {
    # Title and branding
    "site_title": "Tu Voz en Ruta Admin",
    "site_header": "Tu Voz en Ruta",
    "site_brand": "Gestión de Encuestas",
    "site_logo": "images/logo.png",
    "welcome_sign": "Bienvenido al Panel de Administración",
    
    # Icons (FontAwesome)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "interview.Question": "fas fa-question-circle",
        "interview.SurveySubmission": "fas fa-clipboard-check",
        "transport.Unit": "fas fa-bus",
        "transport.Route": "fas fa-route",
    },
    
    # Top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Statistics", "url": "statistical_summary:dashboard"},
        {"model": "auth.User"},
    ],
    
    # User menu (right side)
    "usermenu_links": [
        {"model": "auth.user"},
    ],
    
    # Show/hide elements
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    
    # Theme
    "theme": "flatly",  # cosmo, flatly, darkly, etc.
    "dark_mode_theme": None,
    
    # Custom CSS
    "custom_css": "css/admin_custom.css",
    "custom_js": None,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-info",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
}
```

**Custom Tenant Admin:**

```python
# apps/transport/admin.py
from django.contrib import admin
from django.contrib.admin import AdminSite

class TenantAdminSite(AdminSite):
    """Custom admin site for tenant-specific admin."""
    site_header = "Panel de Administración"
    site_title = "Tu Voz en Ruta Admin"
    index_title = "Bienvenido al Panel de Control"

# Create custom admin site instance
tenant_admin_site = TenantAdminSite(name="tenant_admin")

# Register models with custom admin
@admin.register(Unit, site=tenant_admin_site)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["transit_number", "internal_number", "route", "is_active"]
    list_filter = ["is_active", "route"]
    search_fields = ["transit_number", "internal_number"]
```

---

## Django Best Practices Checklist

**ALWAYS:**

- ✅ Type hints on all views and forms
- ✅ Use `get_object_or_404` instead of try/except
- ✅ Use `reverse_lazy` in class-based views
- ✅ Add `app_name` in urls.py for namespacing
- ✅ Use Django messages framework for feedback
- ✅ Validate data in forms, not views
- ✅ Use `form.is_valid()` before `cleaned_data`
- ✅ Separate public and tenant URLs
- ✅ Use `schema_context` for tenant commands
- ✅ Access tenant via `request.tenant`
- ✅ Use django-jazzmin for enhanced admin UI
- ✅ Customize admin per tenant if needed

**NEVER:**

- ❌ Hard-code URLs (use `reverse()`)
- ❌ Put business logic in views
- ❌ Skip form validation
- ❌ Mix public and tenant logic
- ❌ Forget to add jazzmin before django.contrib.admin
