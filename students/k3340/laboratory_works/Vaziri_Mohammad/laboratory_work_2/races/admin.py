"""Django-admin: администратор задаёт время заездов и результаты."""
from django.contrib import admin
from django.db.models import Count

from .models import Comment, Heat, Race, Racer, Registration, Result, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)


@admin.register(Racer)
class RacerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "team", "racer_class", "experience_years", "user")
    list_filter = ("racer_class", "team")
    search_fields = ("full_name", "team__name", "user__username")


class HeatInline(admin.TabularInline):
    model = Heat
    extra = 0
    fields = ("number", "name", "start_time", "laps")
    show_change_link = True


class RegistrationInline(admin.TabularInline):
    model = Registration
    extra = 0
    fields = ("racer", "car_number", "car_description")
    autocomplete_fields = ("racer",)


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "date", "registration_open", "participants")
    list_filter = ("registration_open",)
    search_fields = ("title", "track")
    date_hierarchy = "date"
    inlines = [HeatInline, RegistrationInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(participants_count=Count("registrations"))

    @admin.display(description="Участников", ordering="participants_count")
    def participants(self, obj):
        return obj.participants_count


class ResultInline(admin.TabularInline):
    model = Result
    extra = 0
    fields = ("registration", "position", "finish_time", "status")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # в выпадающем списке только участники гонки этого заезда
        if db_field.name == "registration":
            heat_id = request.resolver_match.kwargs.get("object_id")
            if heat_id:
                kwargs["queryset"] = Registration.objects.filter(race__heats__pk=heat_id).select_related("racer")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Heat)
class HeatAdmin(admin.ModelAdmin):
    list_display = ("__str__", "race", "number", "start_time", "laps")
    list_editable = ("start_time",)
    list_filter = ("race",)
    list_select_related = ("race",)
    inlines = [ResultInline]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("race", "car_number", "racer", "car_description", "created_at")
    list_filter = ("race",)
    search_fields = ("racer__full_name", "car_description")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("heat", "registration", "position", "finish_time", "status")
    list_editable = ("position", "finish_time", "status")
    list_filter = ("heat__race", "status")
    list_select_related = ("heat__race", "registration__racer")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("race", "author", "comment_type", "rating", "heat_date", "created_at")
    list_filter = ("comment_type", "race")
    search_fields = ("text", "author__username")
