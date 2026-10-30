from django.contrib import admin

from .models import (
    Accommodation, CleaningSchedule, Employee, Floor, Guest, Room, RoomType, Stay,
)


class ReadOnlyAdmin(admin.ModelAdmin):
    # Изменения выполняются через API с проверками бизнес-правил.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Room)
class RoomAdmin(ReadOnlyAdmin):
    list_display = ("number", "floor", "room_type", "phone")
    list_filter = ("floor", "room_type")
    search_fields = ("number",)


@admin.register(Accommodation)
class AccommodationAdmin(ReadOnlyAdmin):
    list_display = ("room", "check_in", "planned_check_out", "actual_check_out", "price_per_night")
    list_filter = ("room",)


@admin.register(CleaningSchedule)
class CleaningScheduleAdmin(ReadOnlyAdmin):
    list_display = ("employee", "floor", "weekday", "valid_from", "valid_to")
    list_filter = ("weekday", "floor")


admin.site.register([RoomType, Employee, Stay], ReadOnlyAdmin)
admin.site.register([Floor, Guest])
