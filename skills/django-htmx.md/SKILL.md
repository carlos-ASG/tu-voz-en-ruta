---
name: django-htmx
description: >
  HTMX and django-htmx integration patterns for building modern, interactive Django applications without complex JavaScript.
  Trigger: When implementing interactive features, partial page updates, or dynamic forms in Django using HTMX.
license: Apache-2.0
metadata:
  author: Carlos
  version: "1.1"
  scope: [root]
  auto_invoke: "Writing HTMX-powered Django views/templates"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
---

## ⚠️ CRITICAL: Class-Based Views Only

**All Django views in this project MUST use Class-Based Views (CBV). Function-Based Views are prohibited.**

## What is HTMX?

HTMX allows you to access AJAX, CSS Transitions, WebSockets, and Server Sent Events directly in HTML using attributes. Build modern, interactive UIs without writing JavaScript.

**Key Benefits:**

- No JavaScript framework needed (React, Vue, etc.)
- Server-side rendering with Django templates
- Minimal client-side code
- Progressive enhancement
- Works seamlessly with Django forms and CSRF

## Installation

```bash
pip install django-htmx
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django_htmx",
]

MIDDLEWARE = [
    # ...
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",  # Add after CSRF
    # ...
]
```

## Base Template Setup

```html
<!-- templates/base.html -->
{% load django_htmx %}
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{% block title %}My App{% endblock %}</title>
    {% htmx_script %}  <!-- Include HTMX -->
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
    {% block content %}{% endblock %}
</body>
</html>
```

## Core HTMX Attributes

```html
<!-- hx-get: Make GET request -->
<button hx-get="/api/users/" hx-target="#results">
    Load Users
</button>

<!-- hx-post: Make POST request -->
<form hx-post="/users/create/" hx-target="#user-list">
    <input name="name" type="text">
    <button type="submit">Create</button>
</form>

<!-- hx-delete: Make DELETE request -->
<button hx-delete="/users/1/" hx-target="#user-list">
    Delete
</button>

<!-- hx-target: Where to put the response -->
<button hx-get="/users/" hx-target="#results">Load</button>
<div id="results"></div>

<!-- hx-swap: How to swap content -->
innerHTML   - Replace inner HTML (default)
outerHTML   - Replace entire element
beforebegin - Insert before element
afterbegin  - Insert as first child
beforeend   - Insert as last child
afterend    - Insert after element

<button hx-get="/users/"
        hx-target="#results"
        hx-swap="innerHTML">
    Replace Inner
</button>

<!-- hx-trigger: When to make request -->
<input hx-get="/search"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#results">

<!-- Common triggers -->
click      - On click (default for buttons)
change     - On value change (default for inputs)
keyup      - On key release
submit     - On form submit (default for forms)
load       - On page load
revealed   - When element scrolls into view
every 2s   - Poll every 2 seconds

<!-- hx-indicator: Show loading state -->
<button hx-get="/api/users/" hx-indicator="#spinner">
    Load Users
</button>
<div id="spinner" class="htmx-indicator">Loading...</div>

<style>
.htmx-indicator { display: none; }
.htmx-request .htmx-indicator { display: inline-block; }
</style>

<!-- hx-confirm: Confirmation dialog -->
<button hx-delete="/users/1/" hx-confirm="Are you sure?">
    Delete
</button>
```

## Django Class-Based Views for HTMX

**CRITICAL**: Use Class-Based Views (CBV) exclusively, as per project standards.

```python
from django.views.generic import ListView, CreateView, DeleteView, TemplateView
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from typing import Any

class UserListView(ListView):
    """View that works for both full page and HTMX requests."""
    model = User
    context_object_name = "users"
    
    def get_template_names(self):
        # Return partial template for HTMX requests
        if self.request.htmx:
            return ["users/_user_list.html"]
        # Return full page for regular requests
        return ["users/list.html"]

class UserDeleteView(DeleteView):
    """Delete user and return updated list via HTMX."""
    model = User
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        
        # Return updated user list for HTMX
        users = User.objects.all()
        return render(request, "users/_user_list.html", {"users": users})

class UserCreateView(CreateView):
    """Create user via HTMX form."""
    model = User
    form_class = UserForm
    template_name = "users/_user_form.html"
    
    def form_valid(self, form):
        """Return new user row for HTMX."""
        user = form.save()
        return render(self.request, "users/_user_row.html", {"user": user})
    
    def form_invalid(self, form):
        """Return form with errors for HTMX."""
        return render(self.request, self.template_name, {"form": form})
```

**Alternative Pattern - Using TemplateView for Custom Logic:**

```python
class UserSearchView(TemplateView):
    """Search users with HTMX live search."""
    template_name = "users/_user_list.html"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        
        if query:
            context["users"] = User.objects.filter(name__icontains=query)
        else:
            context["users"] = User.objects.all()
        
        return context
```

## Template Patterns

```html
<!-- templates/users/list.html - Full page -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Users</h1>

    <!-- User list partial -->
    <div id="user-list">
        {% include "users/_user_list.html" %}
    </div>
</div>
{% endblock %}

<!-- templates/users/_user_list.html - Partial -->
<table>
    <tbody>
        {% for user in users %}
            {% include "users/_user_row.html" %}
        {% endfor %}
    </tbody>
</table>

<!-- templates/users/_user_row.html - Single row -->
<tr id="user-{{ user.id }}">
    <td>{{ user.name }}</td>
    <td>{{ user.email }}</td>
    <td>
        <button hx-delete="{% url 'user_delete' user.id %}"
                hx-target="#user-list"
                hx-confirm="Delete {{ user.name }}?">
            Delete
        </button>
    </td>
</tr>

<!-- templates/users/_user_form.html - Form partial -->
<form hx-post="{% url 'user_create' %}"
      hx-target="#user-list tbody"
      hx-swap="beforeend">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Create User</button>
</form>
```

## django-htmx Middleware Features

```python
from django.views.generic import TemplateView
from typing import Any

class MyView(TemplateView):
    template_name = "my_template.html"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Check if request is from HTMX
        if self.request.htmx:
            context["is_htmx"] = True
        
        # Check if request is boosted
        if self.request.htmx and self.request.htmx.boosted:
            context["is_boosted"] = True
        
        # Get HTMX request metadata
        if self.request.htmx:
            context["current_url"] = self.request.htmx.current_url
            context["target"] = self.request.htmx.target
            context["trigger"] = self.request.htmx.trigger
        
        return context
```

## django-htmx HTTP Response Helpers

```python
from django.views.generic import FormView, TemplateView
from django_htmx.http import (
    HttpResponseClientRedirect,
    HttpResponseLocation,
    trigger_client_event,
)
from django.shortcuts import render

class UserFormView(FormView):
    """Form view with HTMX redirect on success."""
    form_class = UserForm
    template_name = "users/_user_form.html"
    
    def form_valid(self, form):
        form.save()
        # Client-side redirect (full page reload)
        return HttpResponseClientRedirect("/dashboard/")

class UserDetailView(TemplateView):
    """Detail view with HTMX location redirect."""
    template_name = "users/detail.html"
    
    def post(self, request, *args, **kwargs):
        # Process action...
        # Location redirect (HTMX boosted request)
        return HttpResponseLocation("/dashboard/")

class UserCreateEventView(CreateView):
    """Create user and trigger client-side event."""
    model = User
    form_class = UserForm
    template_name = "users/_user_form.html"
    
    def form_valid(self, form):
        user = form.save()
        response = render(self.request, "users/_user_row.html", {"user": user})
        # Trigger client-side event with data
        return trigger_client_event(
            response,
            "userCreated",
            {"userId": user.id, "name": user.name}
        )
```

## Out-of-Band Swaps

```html
<!-- Update multiple parts of page at once -->
<!-- Main content (goes to hx-target) -->
<div id="user-detail">
    <h2>{{ user.name }}</h2>
</div>

<!-- Out-of-band swap (updates different element) -->
<div id="notification-count" hx-swap-oob="true">
    {{ notifications|length }} new notifications
</div>
```

## URL Configuration for HTMX Views

```python
# users/urls.py
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.UserListView.as_view(), name="user_list"),
    path("create/", views.UserCreateView.as_view(), name="user_create"),
    path("<int:pk>/delete/", views.UserDeleteView.as_view(), name="user_delete"),
    path("search/", views.UserSearchView.as_view(), name="user_search"),
]
```

## Best Practices Checklist

**ALWAYS:**

- ✅ **Use Class-Based Views (CBV) for HTMX endpoints**
- ✅ Include CSRF token in HTMX requests (via `hx-headers`)
- ✅ Use `request.htmx` to detect HTMX requests
- ✅ Return partial templates for HTMX, full pages for regular requests
- ✅ Override `get_template_names()` to switch between full/partial templates
- ✅ Use semantic HTML and proper HTTP methods (GET, POST, DELETE)
- ✅ Add loading indicators with `hx-indicator`
- ✅ Use `hx-confirm` for destructive actions
- ✅ Debounce input events with `delay:500ms`
- ✅ Test with and without JavaScript enabled
- ✅ Use `django-htmx` helpers for redirects and events

**NEVER:**

- ❌ **Use Function-Based Views (use CBV instead)**
- ❌ Skip CSRF protection on POST/DELETE requests
- ❌ Return full HTML pages for HTMX requests
- ❌ Forget to handle form validation errors
- ❌ Use polling without stop conditions
