from django.contrib import admin

from .models import Booking, Hotel, Review, Room


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "address"]
    search_fields = ["name", "address"]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["hotel", "number", "room_type", "price", "capacity"]
    list_filter = ["hotel", "room_type"]
    search_fields = ["number", "hotel__name"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "room",
        "arrival",
        "departure",
        "status",
        "checked_in_at",
        "checked_out_at",
    ]
    list_filter = ["status", "room__hotel"]
    search_fields = ["user__username", "room__hotel__name"]
    list_select_related = ["user", "room__hotel"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "room", "rating", "arrival", "departure"]
    list_filter = ["rating", "room__hotel"]


admin.site.site_header = "Отели · Управление"
