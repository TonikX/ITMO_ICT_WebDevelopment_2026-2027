from django.contrib import admin
from .models import Driver, Race, Entry, Heat, Comment


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ['title', 'track', 'start_date', 'status']
    list_filter = ['status', 'start_date']
    search_fields = ['title', 'track']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'team', 'racing_class', 'experience']
    search_fields = ['full_name', 'team']
    list_filter = ['racing_class']


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['race', 'driver', 'number']
    list_filter = ['race']
    autocomplete_fields = ['race', 'driver']
    search_fields = ['driver__full_name']


@admin.register(Heat)
class HeatAdmin(admin.ModelAdmin):
    list_display = ['entry', 'attempt', 'started_at', 'duration', 'position', 'status']
    list_filter = ['entry__race', 'status']
    search_fields = ['entry__driver__full_name']
    autocomplete_fields = ['entry']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['race', 'author', 'kind', 'rating', 'created_at']
    list_filter = ['race', 'kind', 'rating']
    search_fields = ['text', 'author__username']

admin.site.site_header = 'APEX / Race control'
admin.site.site_title = 'APEX'
admin.site.index_title = 'Управление чемпионатом'
