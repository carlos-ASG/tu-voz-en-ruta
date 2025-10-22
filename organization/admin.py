from django.contrib import admin

from .models import Organization, Route, Unit
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # show organization and is_president in list display
    list_display = ('username', 'email', 'first_name', 'last_name', 'organization', 'is_president', 'is_staff')
    list_display_staff = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_president')
    
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'organization')
    list_filter_staff = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informacion personal', {'fields': ('first_name', 'last_name', 'email', 'organization')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_president')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    fieldsets_without_permissions = (
        (None, {'fields': ('username','password')}),
        ('Informacion personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_staff')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'organization', 'password1', 'password2'),
        }),
    )
    
    add_fieldsets_without_organization = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    def get_fieldsets(self, request, obj=None):
        """ Controla los fieldsets de la vista de EDICIÓN (Change View). """
        if request.user.is_superuser:
            return self.fieldsets

        return self.fieldsets_without_permissions

    def get_add_fieldsets(self, request):
        """ Controla los fieldsets de la vista de CREACIÓN (Add View). """
        if request.user.is_superuser:
            return self.add_fieldsets

        return self.add_fieldsets_without_organization

    def get_queryset(self, request):
        qr = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qr
        
        if request.user.organization:
            return qr.filter(organization=request.user.organization)
        
        return qr.none()
    
    def get_list_filter(self, request):
        """ Muestra solo los filtros aplicables al usuario. """
        if request.user.is_superuser:
            return self.list_filter
        
        return self.list_filter_staff

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        # hide organization from non-superusers
        if not request.user.is_superuser and 'organization' in fields:
            fields.remove('organization')
        return tuple(fields)
    
    def get_list_display(self, request):
        """ Muestra solo las columnas aplicables al usuario. """
        if request.user.is_superuser:
            return self.list_display
        
        return self.list_display_staff

    def save_model(self, request, obj, form, change):
        # Non-superusers cannot set arbitrary organization; force their organization
        if not request.user.is_superuser:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # 1. Súper-Usuario: Ve todo.
        if request.user.is_superuser:
            return qs
            
        return qs.none() # Si no es Súper-Usuario ni tiene organización, no ve nada.

    def has_module_permission(self, request):
        # Solo muestra el modelo si el usuario tiene permiso 'is_superuser' o 'is_staff'
        return request.user.is_superuser or request.user.is_staff


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_at', 'updated_at')
    search_fields = ('name', 'organization__name')
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('metadata',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # 1. Súper-Usuario: Ve todo.
        if request.user.is_superuser:
            return qs

        # 2. Usuario con organización: Solo ve objetos de su organización.
        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(organization=request.user.organization)
            
        return qs.none() # Si no es Súper-Usuario ni tiene organización, no ve nada.

    def save_model(self, request, obj, form, change):
        # Si NO es súper-usuario, forzamos la asignación a su organización
        if not request.user.is_superuser:
            obj.organization = request.user.organization
        
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        # Solo muestra el modelo si el usuario tiene permiso 'is_superuser' o 'is_staff'
        return request.user.is_superuser or request.user.is_staff

    def get_fields(self, request, obj=None):
        """Oculta el campo 'organization' para usuarios no superusuario en el formulario."""
        fields = super().get_fields(request, obj)
        # Asegurarnos de trabajar sobre una lista mutable
        fields = list(fields)
        if not request.user.is_superuser and 'organization' in fields:
            fields.remove('organization')
        return tuple(fields)

    def get_readonly_fields(self, request, obj=None):
        # Mantener los readonly_fields definidos, pero permitir que superusuario los vea
        ro = list(super().get_readonly_fields(request, obj) or [])
        # Si el usuario NO es superusuario, ocultamos organization (ya no está en fields)
        return tuple(ro)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_number', 'route', 'created_at', 'updated_at')
    search_fields = ('unit_number',)
    ordering = ('unit_number',)
    readonly_fields = ('created_at', 'updated_at')
    # hide metadata from admin and prevent editing through admin UI
    exclude = ('metadata',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # 1. Súper-Usuario: Ve todo.
        if request.user.is_superuser:
            return qs

        # 2. Usuario con organización: Solo ve objetos de su organización.
        if request.user.organization:
            return qs.filter(organization=request.user.organization)
            
        return qs.none() # Si no es Súper-Usuario ni tiene organización, no ve nada.

    def save_model(self, request, obj, form, change):
        # Si NO es súper-usuario, forzamos la asignación a su organización
        if not request.user.is_superuser:
            obj.organization = request.user.organization
        
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        # Solo muestra el modelo si el usuario tiene permiso 'is_superuser' o 'is_staff'
        return request.user.is_superuser or request.user.is_staff

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        if not request.user.is_superuser and 'organization' in fields:
            fields.remove('organization')
        return tuple(fields)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Restringir el select de 'route' a las rutas de la organización del usuario si no es superusuario."""
        if db_field.name == 'route' and not request.user.is_superuser:
            # Si el usuario tiene una organización, filtrar por ella; sino, dejar vacío
            if getattr(request.user, 'organization', None):
                kwargs['queryset'] = db_field.related_model.objects.filter(organization=request.user.organization)
            else:
                kwargs['queryset'] = db_field.related_model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
