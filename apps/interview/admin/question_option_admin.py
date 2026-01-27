from unfold.admin import ModelAdmin
from ..models import QuestionOption
from apps.transport.admin import tenant_admin_site


class QuestionOptionAdmin(ModelAdmin):
    list_display = ('question', 'text', 'position', 'created_at')
    search_fields = ('text', 'question__text')
    ordering = ('question', 'position')
    readonly_fields = ('created_at', 'updated_at')

tenant_admin_site.register(QuestionOption, QuestionOptionAdmin)

