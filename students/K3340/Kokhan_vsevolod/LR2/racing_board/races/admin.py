from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    Team,
    Car,
    DriverProfile,
    Race,
    Registration,
    RaceResult,
    Comment,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone',)
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone',)
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'car_number')
    search_fields = ('brand', 'model', 'car_number')


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'car', 'driver_class', 'experience_years')
    list_filter = ('driver_class', 'team')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'team', 'car')


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'is_registration_open')
    list_filter = ('is_registration_open',)
    search_fields = ('name', 'location')
    date_hierarchy = 'start_date'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('driver', 'race', 'status', 'registered_at')
    list_filter = ('status', 'race')
    search_fields = ('driver__user__username', 'race__name')
    raw_id_fields = ('driver', 'race')


@admin.register(RaceResult)
class RaceResultAdmin(admin.ModelAdmin):
    list_display = ('registration', 'heat_number', 'position', 'finish_time', 'points')
    list_filter = ('heat_number',)
    search_fields = ('registration__driver__user__username', 'registration__race__name')
    raw_id_fields = ('registration',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'race', 'comment_type', 'rating', 'created_at')
    list_filter = ('comment_type', 'rating')
    search_fields = ('author__username', 'text')
