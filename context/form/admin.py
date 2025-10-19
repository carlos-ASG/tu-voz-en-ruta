from django.contrib import admin
from .models import QuestionOption, SuverySubmission, Answer, Question, ComplaintReason, Complaint


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


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
	list_display = ('text', 'question', 'position', 'created_at')
	search_fields = ('text', 'question__text')
	ordering = ('question', 'position')
	readonly_fields = ('created_at', 'updated_at')


class ReadOnlyAdminMixin:
	"""Mixin to make an admin read-only: no add/change/delete."""
	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		# allow viewing the change form but not saving changes
		return True

	def has_delete_permission(self, request, obj=None):
		return False

	def get_readonly_fields(self, request, obj=None):
		# mark all model fields as readonly
		return [f.name for f in self.model._meta.fields]

	def save_model(self, request, obj, form, change):
		# prevent saving from admin
		pass

	def save_related(self, request, form, formsets, change):
		# prevent saving related objects from admin
		pass

	def change_view(self, request, object_id, form_url='', extra_context=None):
		extra = extra_context or {}
		extra.update({
			'show_save': False,
			'show_save_and_continue': False,
			'show_save_and_add_another': False,
			'show_delete': False,
		})
		return super().change_view(request, object_id, form_url, extra_context=extra)


@admin.register(SuverySubmission)
class SuverySubmissionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
	list_display = ('unit', 'submitted_at')
	search_fields = ('unit__unit_number',)
	# SuverySubmission model tiene solo: id, unit, submitted_at
	readonly_fields = ('id', 'unit', 'submitted_at')
	ordering = ('-submitted_at',)


@admin.register(Answer)
class AnswerAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
	list_display = ('question', 'selected_options_list', 'text_answer', 'rating_answer', 'created_at')
	search_fields = ('question__text',)
	readonly_fields = ('question', 'text_answer', 'rating_answer', 'created_at')
	ordering = ('-created_at',)

	def selected_options_list(self, obj):
		"""Mostrar opciones seleccionadas (texto) para preguntas tipo choice/multi_choice."""
		return ', '.join(obj.selected_options.values_list('text', flat=True))
	selected_options_list.short_description = 'Opciones seleccionadas'

	def get_readonly_fields(self, request, obj=None):
		# incluir también campos ManyToMany como readonly para evitar widgets editables
		base = super().get_readonly_fields(request, obj) or []
		m2m_fields = [f.name for f in self.model._meta.many_to_many]
		# asegurar que no haya duplicados
		return tuple(dict.fromkeys(list(base) + m2m_fields))


@admin.register(ComplaintReason)
class ComplaintReasonAdmin(admin.ModelAdmin):
	list_display = ('code', 'label', 'created_at')
	search_fields = ('code', 'label')
	readonly_fields = ('created_at',)


@admin.register(Complaint)
class ComplaintAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
	list_display = ('unit', 'reason', 'submitted_at', 'created_at')
	search_fields = ('unit__unit_number', 'reason__label')
	readonly_fields = ('created_at',)
	exclude = ('metadata',)
