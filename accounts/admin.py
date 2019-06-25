from django.contrib import admin
from .models import UserPreferences

class UserPreferencesAdmin(admin.ModelAdmin):
    #   exclude = ('current_usage_mb',)
      readonly_fields = ["user"]

admin.site.register(UserPreferences, UserPreferencesAdmin)
