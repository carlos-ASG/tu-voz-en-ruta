from django.contrib import admin
from ..models import QuestionOption


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'position', 'created_at')
    search_fields = ('text', 'question__text')
    ordering = ('question', 'position')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(organization=request.user.organization)

        return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.organization = request.user.organization

        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        if not request.user.is_superuser and 'organization' in fields:
            fields.remove('organization')
        return tuple(fields)
