from django.contrib import admin
from .models import Airline, Booking, Flight, Review


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('number', 'airline', 'origin', 'destination', 'departure_at', 'direction', 'gate', 'status')
    list_filter = ('airline', 'direction', 'status')
    search_fields = ('number', 'origin', 'destination')
    date_hierarchy = 'departure_at'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('flight', 'passenger_name', 'user', 'seat', 'ticket_number', 'checked_in')
    list_filter = ('checked_in', 'flight')
    search_fields = ('passenger_name', 'ticket_number', 'flight__number', 'user__username')
    autocomplete_fields = ('flight', 'user')
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('flight', 'user', 'flight_date', 'rating', 'created_at')
    list_filter = ('rating',)
    readonly_fields = ('flight_date', 'created_at')

admin.site.site_header = 'Skyboard · управление рейсами'
admin.site.site_title = 'Skyboard'
