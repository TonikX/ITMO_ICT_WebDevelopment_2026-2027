from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Race, RaceComment, RaceEntry, RaceResult, User

admin.site.register(User, UserAdmin)


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "location")
    search_fields = ("title", "location")


@admin.register(RaceEntry)
class RaceEntryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "team_name", "race", "user", "racer_class")
    list_filter = ("race", "racer_class")
    search_fields = ("full_name", "team_name")


@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = ("race", "entry", "place", "finish_time")
    list_filter = ("race",)
    search_fields = ("entry__full_name", "finish_time")


@admin.register(RaceComment)
class RaceCommentAdmin(admin.ModelAdmin):
    list_display = ("race", "author", "comment_type", "rating", "race_date")
    list_filter = ("comment_type", "rating")
