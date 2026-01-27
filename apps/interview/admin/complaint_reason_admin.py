from unfold.admin import ModelAdmin
from ..models import ComplaintReason
from apps.transport.admin import tenant_admin_site



class ComplaintReasonAdmin(ModelAdmin):
    list_display = ('label', 'created_at')
    search_fields = ('label',)
    readonly_fields = ('created_at',)

tenant_admin_site.register(ComplaintReason, ComplaintReasonAdmin)