from django.contrib import admin
from ..models import Answer
from .read_only_admin_mixin import ReadOnlyAdminMixin


@admin.register(Answer)
class AnswerAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('question', 'get_question_type', 'get_answer_display', 'created_at')
    list_filter = ('created_at', 'question', 'question__type')
    search_fields = ('question__text',)
    readonly_fields = ('submission', 'question', 'text_answer', 'rating_answer', 'selected_option', 'created_at')
    ordering = ('-created_at',)

    def get_answer_display(self, obj):
        """Mostrar la respuesta según el tipo de pregunta."""
        if obj.rating_answer is not None:
            return f'⭐ {obj.rating_answer}/5'
        elif obj.text_answer:
            text_preview = obj.text_answer[:50]
            return f'💬 {text_preview}{"..." if len(obj.text_answer) > 50 else ""}'
        elif obj.selected_option:
            return f'✓ {obj.selected_option.text}'
        elif obj.selected_options.exists():
            options = ', '.join(obj.selected_options.values_list('text', flat=True))
            return f'☑ {options}'
        return '(Sin respuesta)'
    get_answer_display.short_description = 'Respuesta'

    def get_question_type(self, obj):
        """Mostrar el tipo de pregunta."""
        return obj.question.get_type_display()
    get_question_type.short_description = 'Tipo de pregunta'

    def get_readonly_fields(self, request, obj=None):
        # incluir también campos ManyToMany como readonly para evitar widgets editables
        base = super().get_readonly_fields(request, obj) or []
        m2m_fields = [f.name for f in self.model._meta.many_to_many]
        # asegurar que no haya duplicados
        return tuple(dict.fromkeys(list(base) + m2m_fields))

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
        return tuple(fields)
