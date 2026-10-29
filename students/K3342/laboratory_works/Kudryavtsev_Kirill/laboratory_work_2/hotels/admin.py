from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Booking, Hotel, Review, Room


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'owner']
    search_fields = ['name', 'city']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'number', 'room_type', 'price', 'capacity']
    list_filter = ['hotel', 'room_type']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'arrival', 'departure', 'status']
    list_filter = ['status', 'room__hotel']
    readonly_fields = ['status', 'checked_in_at', 'checked_out_at', 'created_at']
    actions = ['check_in', 'check_out']

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj and obj.status != Booking.BOOKED:
            fields += ['room', 'user', 'arrival', 'departure', 'guests']
        return fields

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            Room.objects.select_for_update().get(pk=obj.room_id)
            obj.full_clean()
            super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) and (obj is None or obj.status == Booking.BOOKED)

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def transition(self, request, queryset, action):
        for initial in queryset:
            with transaction.atomic():
                Room.objects.select_for_update().get(pk=initial.room_id)
                obj = Booking.objects.select_for_update().get(pk=initial.pk)
                try:
                    obj.change_status(action)
                    self.message_user(request, f'{obj}: {obj.get_status_display()}')
                except ValidationError as error:
                    self.message_user(request, ' '.join(error.messages), level=messages.ERROR)

    @admin.action(description='Заселить выбранных гостей')
    def check_in(self, request, queryset):
        self.transition(request, queryset, 'checkin')

    @admin.action(description='Выселить выбранных гостей')
    def check_out(self, request, queryset):
        self.transition(request, queryset, 'checkout')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'rating', 'arrival', 'departure']
    readonly_fields = ['booking', 'room', 'user', 'arrival', 'departure', 'created_at']

    def has_add_permission(self, request):
        return False
