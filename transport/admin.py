from django.contrib import admin


from .models import Route, Unit


class TenantAdminSite(admin.AdminSite):
    """
    Custom AdminSite for managing transport (routes, units, users).
    """
    site_header = "Administración de Transporte"
    site_title = "Administración de Transporte"
    index_title = "Panel de Administración de Transporte"

# class UserAdmin(TenantAdminMixin, admin.ModelAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     ordering = ('username',)
#     readonly_fields = ('date_joined', 'last_login')

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
#tenant_admin_site.register(User, UserAdmin)
