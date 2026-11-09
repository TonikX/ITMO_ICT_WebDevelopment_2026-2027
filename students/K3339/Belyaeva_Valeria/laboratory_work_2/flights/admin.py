from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Booking, Flight, Review, User


@admin.register(User)
class PassengerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Дополнительные сведения', {'fields': ('birth_date', 'passport_number', 'home_address', 'nationality')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Дополнительные сведения', {'fields': ('birth_date', 'passport_number', 'home_address', 'nationality')}),)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['number', 'origin', 'destination', 'departure_at', 'gate', 'status']
    list_filter = ['kind', 'status', 'airline']
    search_fields = ['number', 'origin', 'destination']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['passenger_name', 'flight', 'seat', 'ticket_number', 'checked_in']
    list_filter = ['checked_in', 'flight']
    search_fields = ['passenger_name', 'ticket_number']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['flight', 'user', 'rating', 'flight_date']


admin.site.site_header = 'Nordline · управление полётами'
admin.site.site_title = 'Nordline'
