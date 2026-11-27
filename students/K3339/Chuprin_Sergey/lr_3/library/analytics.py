from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    Book,
    BookCopy,
    Reader,
    Loan,
    ReaderRoomHistory,
)

# какие книги закреплены за заданным читателем
def get_reader_books(reader):
    book_ids = Loan.objects.filter(
        reader=reader,
        return_date__isnull=True,
        book_copy__scrapped_at__isnull=True
    ).values('book_copy__book_id')

    return Book.objects.filter(pk__in=book_ids)


# кто из читатлей взял книгу более месяца назад
def get_overdue_readers():
    today = timezone.localdate()

    previous_month = today.replace(day=1) - timedelta(days=1)

    cutoff = previous_month.replace(
        day=min(today.day, previous_month.day)
    )

    reader_ids = Loan.objects.filter(
        issued_date__lt=cutoff,
        return_date__isnull=True
    ).values('reader_id')

    return Reader.objects.filter(pk__in=reader_ids)


# за кем закреплены книги, количество экзампляров которых <= 2
def get_rare_book_readers():
    rare_books = (
        BookCopy.objects
        .filter(scrapped_at__isnull=True)
        .values('book_id')
        .annotate(total=Count('id'))
        .filter(total__lte=2)
        .values('book_id')
    )

    reader_ids = Loan.objects.filter(
        book_copy__book_id__in=rare_books,
        book_copy__scrapped_at__isnull=True,
        return_date__isnull=True
    ).values('reader_id')

    return Reader.objects.filter(pk__in=reader_ids)


def get_active_readers():
    reader_ids = ReaderRoomHistory.objects.filter(
        end_date__isnull=True
    ).values('reader_id')

    return Reader.objects.filter(pk__in=reader_ids)


# сколько читателей младше 20
def get_young_readers_count():
    today = timezone.localdate()

    try:
        cutoff = today.replace(year=today.year - 20)
    except ValueError:
        cutoff = today.replace(
            year=today.year - 20,
            day=28
        )

    return get_active_readers().filter(
        date_of_birth__gt=cutoff,
        date_of_birth__lte=today
    ).count()


# процентная статистика образования читатейлей
def get_education_statistics():
    readers = get_active_readers()

    statistics = readers.aggregate(
        total=Count('id'),

        primary=Count(
            'id',
            filter=Q(education=Reader.Education.PRIMARY)
        ),

        secondary=Count(
            'id',
            filter=Q(education=Reader.Education.SECONDARY)
        ),

        higher=Count(
            'id',
            filter=Q(education=Reader.Education.HIGHER)
        ),

        academic_degree=Count(
            'id',
            filter=Q(has_academic_degree=True)
        )
    )

    total = statistics['total']

    return {
        'total_readers': total,

        'primary': percentage(statistics['primary'], total),
        'secondary': percentage(statistics['secondary'], total),
        'higher': percentage(statistics['higher'], total),
        'academic_degree': percentage(
            statistics['academic_degree'], total
        )
    }


def percentage(count, total):
    return round(count / total * 100, 2) if total else 0