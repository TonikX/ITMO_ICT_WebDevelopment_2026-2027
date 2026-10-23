from django.contrib import admin
from .models import User, Auto, Race, Result, Registration, Comment
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Гонщик", {"fields": ("racer_class", "team", "birthday", "driving_experience")}),)
    list_display = ("username", "first_name", "last_name", "team", "racer_class", "is_staff", "birthday", "driving_experience")


@admin.register(Auto)
class AutoAdmin(admin.ModelAdmin):
    list_display = ("state", "make", "model", "color", "owner")
    search_fields = ("state", "make", "model")


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "date", "start_time", "end_time", "location")
    list_filter = ("date", "location")
    search_fields = ("name", "date", "location")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "auto", "duration")
    list_filter = ("race", "user")
    search_fields = ("user", "race")


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "created_at")
    list_filter = ("race", "user")
    search_fields = ("user", "race", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "text", "race_date", "comment_type", "rating", "created_at")
    list_filter = ("comment_type", "race")
    search_fields = ("text", "user", "race")
