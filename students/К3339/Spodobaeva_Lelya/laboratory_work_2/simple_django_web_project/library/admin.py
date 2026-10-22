from django.contrib import admin

from .models import Reservation, Review, Tour


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ("name", "agency", "country", "start_date", "end_date", "price")
    search_fields = ("name", "agency", "country")
    list_filter = ("country", "agency")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("tour", "user", "tourists_count", "is_confirmed", "created_at")
    list_filter = ("is_confirmed", "tour__country")
    search_fields = ("tour__name", "user__username")
    actions = ["confirm_reservations"]

    @admin.action(description="Подтвердить выбранные бронирования")
    def confirm_reservations(self, request, queryset):
        queryset.update(is_confirmed=True)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("tour", "user", "rating", "tour_start_date", "tour_end_date")
    list_filter = ("rating", "tour__country")
    search_fields = ("tour__name", "user__username", "text")
