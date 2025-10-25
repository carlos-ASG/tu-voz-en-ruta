from django.contrib import admin
from ..models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'type', 'position', 'active', 'created_at', 'updated_at')
    list_filter = ('type', 'active')
    search_fields = ('text',)
    ordering = ('position',)
    readonly_fields = ('created_at', 'updated_at')

    def text_short(self, obj):
        return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Texto (resumen)'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(Organization=request.user.organization)

        return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.Organization = request.user.organization

        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        # field is named 'Organization' in the model (note the capital O)
        if not request.user.is_superuser and 'Organization' in fields:
            fields.remove('Organization')
        return tuple(fields)
