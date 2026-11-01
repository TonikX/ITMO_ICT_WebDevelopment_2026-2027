from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Conference, Participation, Review, Topic, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Профиль", {"fields": ("organization", "academic_degree")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Профиль", {"fields": ("organization", "academic_degree")}),)
    list_display = ("username", "last_name", "first_name", "organization", "is_staff")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "start_date", "end_date")
    list_filter = ("topics", "city")
    search_fields = ("title", "description")
    filter_horizontal = ("topics",)


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("user", "conference", "result")
    list_filter = ("result", "conference")
    list_editable = ("result",)
    search_fields = ("talk_title", "user__username", "user__last_name")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("conference", "author", "rating", "created_at")
    list_filter = ("rating", "conference")
