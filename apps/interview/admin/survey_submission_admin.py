from django.contrib import admin
from ..models import SurveySubmission
from .read_only_admin_mixin import ReadOnlyAdminMixin


""" @admin.register(SurveySubmission)
class SurveySubmissionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('unit', 'submitted_at')
    # ✅ Cambiar 'unit__unit_number' por 'unit__transit_number'
    search_fields = ('unit__transit_number',)
    # SurveySubmission model tiene solo: id, unit, submitted_at
    readonly_fields = ('id', 'unit', 'submitted_at')
    ordering = ('-submitted_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if hasattr(request.user, 'organization') and request.user.organization:
            return qs.filter(organization=request.user.organization)

        return qs.none()

    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.is_staff

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields = list(fields)
        if not request.user.is_superuser and 'organization' in fields:
            fields.remove('organization')
        return fields """