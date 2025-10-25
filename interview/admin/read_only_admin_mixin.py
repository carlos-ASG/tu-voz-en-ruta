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
