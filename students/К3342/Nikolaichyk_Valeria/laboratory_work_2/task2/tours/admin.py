from django.contrib import admin
from .models import Tour, Booking, Review


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'agency', 'country', 'start_date', 'end_date', 'price')
    list_filter = ('country', 'agency')
    search_fields = ('title', 'country', 'agency')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'booking_date', 'places', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'tour__title')

    actions = ['confirm_bookings']

    @admin.action(description='Подтвердить выбранные бронирования')
    def confirm_bookings(self, request, queryset):
        queryset.update(status=Booking.Status.CONFIRMED)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('tour', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('tour__title', 'user__username')