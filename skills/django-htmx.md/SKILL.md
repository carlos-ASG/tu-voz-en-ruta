---
name: django-htmx
description: >
  HTMX and django-htmx integration patterns for building modern, interactive Django applications without complex JavaScript.
  Trigger: When implementing interactive features, partial page updates, or dynamic forms in Django using HTMX.
license: Apache-2.0
metadata:
  author: Carlos
  version: "1.0"
  scope: [root]
  auto_invoke: "Writing HTMX-powered Django views/templates"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, WebFetch, WebSearch, Task
---

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

## Django Views for HTMX

```python
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404

def user_list(request: HttpRequest) -> HttpResponse:
    """View that works for both full page and HTMX requests."""
    users = User.objects.all()

    # Check if request is from HTMX
    if request.htmx:
        # Return only the partial template
        template_name = "users/_user_list.html"
    else:
        # Return full page
        template_name = "users/list.html"

    return render(request, template_name, {"users": users})

def user_delete(request: HttpRequest, user_id: int) -> HttpResponse:
    """Delete user and return updated list."""
    user = get_object_or_404(User, id=user_id)
    user.delete()

    # Return updated user list
    users = User.objects.all()
    return render(request, "users/_user_list.html", {"users": users})

def user_create(request: HttpRequest) -> HttpResponse:
    """Create user via HTMX form."""
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Return new user row
            return render(request, "users/_user_row.html", {"user": user})
        # Return form with errors
    else:
        form = UserForm()

    return render(request, "users/_user_form.html", {"form": form})
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
from django.http import HttpRequest, HttpResponse

def my_view(request: HttpRequest) -> HttpResponse:
    # Check if request is from HTMX
    if request.htmx:
        # HTMX request
        pass

    # Check if request is boosted
    if request.htmx.boosted:
        pass

    # Get current URL in browser
    current_url = request.htmx.current_url

    # Get target element ID
    target = request.htmx.target

    # Get trigger element ID
    trigger = request.htmx.trigger
```

## django-htmx HTTP Response Helpers

```python
from django_htmx.http import (
    HttpResponseClientRedirect,
    HttpResponseLocation,
    trigger_client_event,
)

# Client-side redirect (full page reload)
def my_view(request: HttpRequest) -> HttpResponse:
    return HttpResponseClientRedirect("/dashboard/")

# Location redirect (HTMX boosted request)
def my_view(request: HttpRequest) -> HttpResponse:
    return HttpResponseLocation("/dashboard/")

# Trigger client-side event
def my_view(request: HttpRequest) -> HttpResponse:
    response = render(request, "template.html", {})
    return trigger_client_event(
        response,
        "userCreated",
        {"userId": 123, "name": "Carlos"}
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

## Best Practices Checklist

**ALWAYS:**

- ✅ Include CSRF token in HTMX requests (via `hx-headers`)
- ✅ Use `request.htmx` to detect HTMX requests
- ✅ Return partial templates for HTMX, full pages for regular requests
- ✅ Use semantic HTML and proper HTTP methods (GET, POST, DELETE)
- ✅ Add loading indicators with `hx-indicator`
- ✅ Use `hx-confirm` for destructive actions
- ✅ Debounce input events with `delay:500ms`
- ✅ Test with and without JavaScript enabled
- ✅ Use `django-htmx` helpers for redirects and events

**NEVER:**

- ❌ Skip CSRF protection on POST/DELETE requests
- ❌ Return full HTML pages for HTMX requests
- ❌ Forget to handle form validation errors
- ❌ Use polling without stop conditions
