from django.contrib import admin
from ..models import ComplaintReason
from transport.admin import tenant_admin_site



class ComplaintReasonAdmin(admin.ModelAdmin):
    list_display = ('label', 'created_at')
    search_fields = ('label',)
    readonly_fields = ('created_at',)

tenant_admin_site.register(ComplaintReason, ComplaintReasonAdmin)