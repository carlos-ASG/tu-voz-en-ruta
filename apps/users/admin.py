from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin para el modelo de usuario personalizado.
    Registrado en el admin público (super-admin).
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login')

    # Agregar el campo organization a los fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'is_staff', 'is_active'),
        }),
    )
    


