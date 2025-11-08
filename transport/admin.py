from django.contrib import admin
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _


from .models import Route, Unit

User = get_user_model()


class TenantAdminSite(admin.AdminSite):
    """
    Custom AdminSite for managing transport (routes, units, users).
    """
    site_header = "Administración de Transporte"
    site_title = "Administración de Transporte"
    index_title = "Panel de Administración de Transporte"


# class UserAdmin(admin.ModelAdmin):
#     """
#     Admin para usuarios en el panel de tenant.
#     """
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     list_filter = ('is_staff', 'is_active')
#     ordering = ('username',)
#     readonly_fields = ('date_joined', 'last_login')
    
#     # Agregar el campo organization a los fieldsets
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         (_('Información personal'), {'fields': ('first_name', 'last_name', 'email')}),
#         (_('Permisos'), {
#             'fields': ('is_active', 'is_staff'),
#         }),
#         (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'password1', 'password2', 'email', 'is_staff', 'is_active'),
#         }),
#     )
    
#     def get_queryset(self, request):
#         """Filtra usuarios para que solo muestre los de este tenant."""
#         qs = super().get_queryset(request)
#         return qs.filter(organization=request.tenant)

#     def save_model(self, request, obj, form, change):
#         """Asigna automáticamente el tenant al crear un usuario."""
#         if not change:
#             obj.organization = request.tenant
#         super().save_model(request, obj, form, change)

class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('metadata',)

class UnitAdmin(admin.ModelAdmin):
    list_display = ('transit_number', 'internal_number', 'owner', 'route', 'created_at', 'updated_at')
    search_fields = ('transit_number', 'internal_number', 'owner')
    ordering = ('transit_number', 'internal_number', 'owner')
    readonly_fields = ('created_at', 'updated_at')
    # hide metadata from admin and prevent editing through admin UI
    exclude = ('metadata',)


tenant_admin_site = TenantAdminSite(name='transport_admin')
tenant_admin_site.register(Route, RouteAdmin)
tenant_admin_site.register(Unit, UnitAdmin)
# tenant_admin_site.register(User, UserAdmin)
