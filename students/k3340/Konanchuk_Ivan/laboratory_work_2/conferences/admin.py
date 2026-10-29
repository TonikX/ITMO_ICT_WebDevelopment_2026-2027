from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Conference, Participation, Review, Topic, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Научные данные", {"fields": ("organization", "academic_degree")}),
    )
    list_display = ["username", "last_name", "first_name", "organization", "is_staff"]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ["name", "venue", "start_date", "end_date"]
    list_filter = ["topics"]
    search_fields = ["name", "venue"]
    filter_horizontal = ["topics"]


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ["user", "conference", "talk_title", "result"]
    list_editable = ["result"]
    list_filter = ["result", "conference"]
    search_fields = ["talk_title", "user__last_name"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "conference", "rating", "created_at"]
    list_filter = ["conference", "rating"]
