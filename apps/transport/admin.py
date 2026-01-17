from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin, UserAdmin


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


class TenantUserAdmin(UserAdmin):
    """
    Admin personalizado para usuarios en el panel de tenant.
    Restringe acciones sobre superusuarios para usuarios no-superusuarios.
    """

    def get_fieldsets(self, request, obj=None):
        """
        Oculta los campos is_staff e is_superuser del admin de tenant.
        - is_staff: siempre es True por defecto, no necesita mostrarse
        - is_superuser: solo visible para superusuarios
        """
        fieldsets = super().get_fieldsets(request, obj)

        # Copiamos los fieldsets para no modificar el original
        fieldsets = list(fieldsets)

        # Lista de campos a remover según el usuario
        fields_to_remove = ['is_staff']  # Siempre removemos is_staff

        # Si el usuario actual no es superusuario, también removemos is_superuser
        if not request.user.is_superuser:
            fields_to_remove.append('is_superuser')

        # Buscamos y removemos los campos especificados
        for i, (name, data) in enumerate(fieldsets):
            fields = list(data.get('fields', []))
            original_length = len(fields)

            # Removemos los campos de la lista
            fields = [f for f in fields if f not in fields_to_remove]

            # Si se removieron campos, actualizamos el fieldset
            if len(fields) != original_length:
                fieldsets[i] = (name, {**data, 'fields': tuple(fields)})

        return fieldsets

    def has_delete_permission(self, request, obj=None):
        """
        Impide que usuarios no-superusuarios eliminen superusuarios.
        """
        # Primero verificamos el permiso base
        base_permission = super().has_delete_permission(request, obj)

        # Si no tiene permiso base o no hay objeto específico, retornamos lo estándar
        if not base_permission or obj is None:
            return base_permission

        # Si el usuario a borrar es superusuario y el usuario actual NO es superusuario
        if obj.is_superuser and not request.user.is_superuser:
            return False

        return True

    def has_change_permission(self, request, obj=None):
        """
        Impide que usuarios no-superusuarios modifiquen superusuarios.
        """
        # Primero verificamos el permiso base
        base_permission = super().has_change_permission(request, obj)

        # Si no tiene permiso base o no hay objeto específico, retornamos lo estándar
        if not base_permission or obj is None:
            return base_permission

        # Si el usuario a modificar es superusuario y el usuario actual NO es superusuario
        if obj.is_superuser and not request.user.is_superuser:
            return False

        return True

    def save_model(self, request, obj, form, change):
        """
        Marca automáticamente como staff a los usuarios nuevos creados desde el tenant admin.
        """
        # Si es un usuario nuevo (no es una modificación), automáticamente lo hacemos staff
        if not change:
            obj.is_staff = True

        super().save_model(request, obj, form, change)


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
tenant_admin_site.register(User, TenantUserAdmin)
tenant_admin_site.register(Group, GroupAdmin)
