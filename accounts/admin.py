from django.contrib.auth.admin import GroupAdmin as origGroupAdmin
from django.contrib.auth.models import Group, User
from django.contrib import admin
from django import forms
from .models import UserPreferences


class GroupAdminForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        User.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Users', False),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            initial_users = self.instance.user_set.values_list('pk', flat=True)
            self.initial['users'] = initial_users

    def save(self, *args, **kwargs):
        kwargs['commit'] = True
        return super(GroupAdminForm, self).save(*args, **kwargs)

    def save_m2m(self):
        self.instance.user_set.clear()
        self.instance.user_set.add(*self.cleaned_data['users'])


class GroupAdmin(origGroupAdmin):
    form = GroupAdminForm
    # Excluding permission until we implement their usage
    exclude = ('permissions',)


class UserPreferencesAdmin(admin.ModelAdmin):
    exclude = ('current_usage_mb',)
    readonly_fields = ["user"]


admin.site.register(UserPreferences, UserPreferencesAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
