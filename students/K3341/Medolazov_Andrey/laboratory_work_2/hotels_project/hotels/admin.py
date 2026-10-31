from django.contrib import admin
from django.utils import timezone

from .models import Amenity, Hotel, Reservation, Review, Room


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ['number', 'room_type', 'price', 'capacity']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'city', 'address']
    list_filter = ['city']
    search_fields = ['name', 'owner', 'address']
    filter_horizontal = ['amenities']
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'hotel', 'room_type', 'price', 'capacity']
    list_filter = ['hotel', 'room_type']
    search_fields = ['number', 'hotel__name']
    filter_horizontal = ['amenities']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'date_from', 'date_to', 'guests', 'status', 'checked_in_at', 'checked_out_at']
    list_filter = ['status', 'room__hotel', 'date_from']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'room__hotel__name']
    date_hierarchy = 'date_from'
    readonly_fields = ['created_at']
    actions = ['check_in', 'check_out']

    @admin.action(description='Заселить выбранных гостей')
    def check_in(self, request, queryset):
        count = queryset.filter(status='booked').update(status='checked_in', checked_in_at=timezone.now())
        self.message_user(request, f'Заселено гостей: {count}')

    @admin.action(description='Выселить выбранных гостей')
    def check_out(self, request, queryset):
        count = queryset.filter(status='checked_in').update(status='checked_out', checked_out_at=timezone.now())
        self.message_user(request, f'Выселено гостей: {count}')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'rating', 'date_from', 'date_to', 'created_at']
    list_filter = ['rating', 'room__hotel']
    search_fields = ['text', 'user__username']
