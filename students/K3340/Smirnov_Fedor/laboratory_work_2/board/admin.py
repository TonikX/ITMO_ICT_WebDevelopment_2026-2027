from django.contrib import admin

from .models import Booking, Comment, Flight


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 1


class FlightAdmin(admin.ModelAdmin):
    list_display = ['number', 'airline', 'kind', 'from_city', 'to_city', 'takeoff', 'gate']
    list_filter = ['kind', 'airline']
    search_fields = ['number', 'airline', 'from_city', 'to_city']
    inlines = [BookingInline]


class BookingAdmin(admin.ModelAdmin):
    list_display = ['flight', 'passenger', 'seat', 'ticket', 'checked_in']
    list_filter = ['checked_in', 'flight']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['flight', 'author', 'flight_date', 'rating']


admin.site.register(Flight, FlightAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Comment, CommentAdmin)
