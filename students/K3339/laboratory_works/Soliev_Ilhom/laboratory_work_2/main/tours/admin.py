from django.contrib import admin

from .models import Agency, Booking, Country, Review, Tour


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email"]
    search_fields = ["name"]


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ["title", "country", "agency", "start_date", "end_date", "price"]
    list_filter = ["country", "agency", "start_date"]
    search_fields = ["title", "description"]
    list_select_related = ["country", "agency"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["tour", "user", "travelers", "status", "created_at"]
    list_filter = ["status", "tour__country"]
    search_fields = ["tour__title", "user__username"]
    list_select_related = ["tour", "user"]
    readonly_fields = ["created_at"]
    actions = ["confirm_bookings"]

    @admin.action(description="Подтвердить выбранные бронирования")
    def confirm_bookings(self, request, queryset):
        count = queryset.update(status=Booking.Status.CONFIRMED)
        self.message_user(request, f"Подтверждено бронирований: {count}.")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["tour", "user", "rating", "start_date", "end_date"]
    list_filter = ["rating"]
    search_fields = ["text", "user__username", "tour__title"]
    list_select_related = ["tour", "user"]
    readonly_fields = ["created_at"]
