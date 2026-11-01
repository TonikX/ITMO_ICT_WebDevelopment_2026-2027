from django.contrib import admin

from .models import Conference, Registration, Review, Topic, Venue


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ["title", "venue", "start_date", "end_date"]
    list_filter = ["topics", "venue__city"]
    search_fields = ["title"]
    filter_horizontal = ["topics"]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["author", "conference", "presentation_title", "result"]
    list_filter = ["conference", "result"]
    list_editable = ["result"]
    search_fields = ["author__username", "presentation_title"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["conference", "author", "rating", "created_at"]
    readonly_fields = ["conference_start", "conference_end", "created_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.conference_start = obj.conference.start_date
            obj.conference_end = obj.conference.end_date
        super().save_model(request, obj, form, change)


admin.site.register(Topic)
admin.site.register(Venue)
admin.site.site_header = "Научные конференции — управление"
