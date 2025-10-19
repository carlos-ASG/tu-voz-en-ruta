from django.contrib import admin
from .models import Unit, Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('metadata',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'route', 'created_at', 'updated_at')
    search_fields = ('unit_number',)
    ordering = ('unit_number',)
    readonly_fields = ('created_at', 'updated_at')
    # hide metadata from admin and prevent editing through admin UI
    exclude = ('metadata',)
