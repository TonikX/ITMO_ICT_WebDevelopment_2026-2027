from datetime import datetime, time

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import (
    Hotel,
    RoomType,
    Amenity,
    Room,
    Reservation,
    Review,
    Stay,
)


admin.site.register(Hotel)
admin.site.register(RoomType)
admin.site.register(Amenity)
admin.site.register(Room)
admin.site.register(Review)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out')
    list_filter = ('room__hotel', 'check_in')
    search_fields = ('user__username', 'room__number')
    actions = ['check_in_guests']

    @admin.action(description='Заселить', permissions=['change'])
    def check_in_guests(self, request, queryset):
        created = 0
        skipped = 0
        for reservation in queryset:
            check_in = timezone.make_aware(
                datetime.combine(reservation.check_in, time.min)
            )
            with transaction.atomic():
                # Блокируем номер, чтобы два запуска действия не создали дубликат.
                Room.objects.select_for_update().get(pk=reservation.room_id)
                stays = Stay.objects.filter(
                    user=reservation.user, room=reservation.room
                )
                if stays.filter(Q(check_out__isnull=True) | Q(check_in=check_in)).exists():
                    skipped += 1
                    continue
                Stay.objects.create(
                    user=reservation.user,
                    room=reservation.room,
                    check_in=check_in,
                )
                created += 1
        if created:
            self.message_user(request, f'Заселено: {created}.', messages.SUCCESS)
        if skipped:
            self.message_user(
                request, f'Уже есть запись о проживании, пропущено: {skipped}.',
                messages.WARNING,
            )


@admin.register(Stay)
class StayAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'room',
        'check_in',
        'check_out',
        'status',
    )

    list_filter = (
        'room',
        'check_in',
        'room__hotel',
        ('check_out', admin.EmptyFieldListFilter),
    )

    list_select_related = ('user', 'room', 'room__hotel')
    actions = ['check_out_guests']

    @admin.display(description='Статус')
    def status(self, obj):
        return 'Завершено' if obj.check_out else 'Проживает'

    @admin.action(description='Выселить', permissions=['change'])
    def check_out_guests(self, request, queryset):
        now = timezone.now()
        updated = queryset.filter(check_out__isnull=True, check_in__lte=now).update(
            check_out=now
        )
        self.message_user(request, f'Выселено: {updated}.', messages.SUCCESS)

    search_fields = (
        'user__username',
        'room__number',
    )
