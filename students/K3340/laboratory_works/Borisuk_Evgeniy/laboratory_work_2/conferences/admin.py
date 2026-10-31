"""Управление конференциями через Django-admin."""

from django.contrib import admin

from .models import Conference, Registration, Review, Topic


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    """Карточки и поиск конференций."""

    list_display = ["title", "location", "start_date", "end_date"]
    search_fields = ["title", "location"]
    filter_horizontal = ["topics"]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """Выставление результатов выступлений."""

    list_display = ["author", "conference", "presentation_title", "result"]
    list_filter = ["result", "conference"]


admin.site.register(Topic)
admin.site.register(Review)
