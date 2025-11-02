from django.contrib import admin
from ..models import Complaint
from transport.admin import tenant_admin_site
from .read_only_admin_mixin import ReadOnlyAdminMixin


class ComplaintAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('unit', 'reason', 'submitted_at', 'created_at')
    # ✅ Cambiar 'unit__unit_number' por 'unit__transit_number'
    search_fields = ('unit__transit_number', 'reason__label')
    readonly_fields = ('created_at',)
    exclude = ('metadata',)

tenant_admin_site.register(Complaint, ComplaintAdmin)