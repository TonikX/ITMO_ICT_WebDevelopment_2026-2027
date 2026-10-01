from django.contrib import admin

from .models import Conference, Registration, Review, Topic

admin.site.register(Topic)
admin.site.register(Conference)
admin.site.register(Review)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'conference', 'talk_title', 'recommended_for_publication']
    list_editable = ['recommended_for_publication']
