from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Race, Registration, Comment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'team', 'driver_class', 'experience', 'is_staff')
    search_fields = ('username', 'team')

    fieldsets = UserAdmin.fieldsets + (
        ('Профиль гонщика', {
            'fields': ('team', 'driver_class', 'experience', 'bio'),
        }),
    )


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'date')
    list_filter = ('date', 'location')
    search_fields = ('name', 'location')
    ordering = ('-date',)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'race', 'race_time', 'result', 'created_at')
    list_filter = ('race',)
    search_fields = ('user__username', 'race__name')
    ordering = ('-created_at',)
    fields = ('user', 'race', 'car_description', 'race_time', 'result')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'race', 'comment_type', 'rating', 'created_at')
    list_filter = ('comment_type', 'rating', 'race')
    search_fields = ('author__username', 'race__name', 'text')
    ordering = ('-created_at',)