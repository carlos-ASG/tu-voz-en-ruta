from django.contrib import admin
from .models import Organization, Director


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_at', 'updated_at')
    search_fields = ('name', 'address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    # añadir columna user y permitir buscar por username/email
    list_display = ('user', 'first_name', 'last_name', 'email', 'organization', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
    list_filter = ('organization',)
    readonly_fields = ('created_at', 'updated_at')