from calendar import monthrange
from datetime import date

from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    ReaderRoom,
    ReaderRoomHistory,
    BookCopyRoomHistory,
)


# считаем число какиъ-то объектов за день
# результат: словарь ключ - id зала, значение - количество объектов
def get_daily_counts(model, object_field, day):
    rows = (
        model.objects
        .filter(start_date__lte=day)
        .filter(
            Q(end_date__gt=day) |
            Q(end_date__isnull=True)
        )
        .values('reader_room_id')
        .annotate(
            total=Count(object_field, distinct=True)
        )
    )

    return {
        row['reader_room_id']: row['total']
        for row in rows
    }


def get_monthly_report(year, month):
    rooms = list(
        ReaderRoom.objects.all().order_by('number')
    )

    today = timezone.localdate()

    days_count = monthrange(year, month)[1]

    if year == today.year and month == today.month:
        days_count = today.day

    first_day = date(year, month, 1)
    last_day = date(year, month, days_count)

    daily_statistics = []

    for day_number in range(1, days_count + 1):
        day = date(year, month, day_number)

        books = get_daily_counts(
            BookCopyRoomHistory,
            'book_copy_id',
            day
        )

        readers = get_daily_counts(
            ReaderRoomHistory,
            'reader_id',
            day
        )

        room_statistics = []

        for room in rooms:
            room_statistics.append({
                'room_id': room.id,
                'room_number': room.number,
                'room_name': room.name,
                'books_count': books.get(room.id, 0),
                'readers_count': readers.get(room.id, 0)
            })

        daily_statistics.append({
            'date': day.isoformat(),
            'total_books': sum(books.values()),
            'total_readers': sum(readers.values()),
            'rooms': room_statistics
        })

    registrations = ReaderRoomHistory.objects.filter(
        reason=ReaderRoomHistory.Reason.REGISTRATION,
        start_date__range=(first_day, last_day)
    )

    registration_counts = (
        registrations
        .values('reader_room_id')
        .annotate(total=Count('reader_id', distinct=True))
    )

    registrations_by_room = {
        row['reader_room_id']: row['total']
        for row in registration_counts
    }

    return {
        'year': year,
        'month': month,
        'daily_statistics': daily_statistics,
        'new_readers': {
            'total': registrations.values(
                'reader_id'
            ).distinct().count(),

            'rooms': [
                {
                    'room_id': room.id,
                    'room_number': room.number,
                    'room_name': room.name,
                    'count': registrations_by_room.get(
                        room.id, 0
                    )
                }
                for room in rooms
            ]
        }
    }