from django.contrib import admin
from ..models import Question
from apps.transport.admin import tenant_admin_site



class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'type', 'position', 'active', 'created_at', 'updated_at')
    list_filter = ('type', 'active')
    search_fields = ('text',)
    ordering = ('position',)
    readonly_fields = ('created_at', 'updated_at')

    def text_short(self, obj):
        return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Texto (resumen)'

tenant_admin_site.register(Question, QuestionAdmin)