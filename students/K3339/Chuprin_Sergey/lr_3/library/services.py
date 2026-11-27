from django.db import transaction
from django.utils import timezone

from .models import Reader, ReaderRoomHistory

from rest_framework.exceptions import ValidationError

from .models import BookCopy, BookCopyRoomHistory, Loan


@transaction.atomic
def register_reader(reader_room, **reader_data):
    today = timezone.localdate()

    reader = Reader.objects.create(
        last_registration_date=today,
        **reader_data
    )

    ReaderRoomHistory.objects.create(
        reader=reader,
        reader_room=reader_room,
        start_date=today,
        reason=ReaderRoomHistory.Reason.REGISTRATION
    )

    return reader


def get_active_reader_history(reader):
    return ReaderRoomHistory.objects.filter(
        reader=reader,
        end_date__isnull=True
    ).first()


@transaction.atomic
def unregister_reader(reader_id):
    reader = Reader.objects.select_for_update().get(pk=reader_id)
    history = get_active_reader_history(reader)

    if history is None:
        raise ValidationError("Читатель уже выписан")

    history.end_date = timezone.localdate()
    history.save(update_fields=['end_date'])


@transaction.atomic
def enroll_reader(reader_id, reader_room):
    reader = Reader.objects.select_for_update().get(pk=reader_id)

    if get_active_reader_history(reader) is not None:
        raise ValidationError("Читатель уже записан")

    today = timezone.localdate()

    ReaderRoomHistory.objects.create(
        reader=reader,
        reader_room=reader_room,
        start_date=today,
        reason=ReaderRoomHistory.Reason.REGISTRATION
    )

    reader.last_registration_date = today
    reader.save(update_fields=['last_registration_date'])

    return reader


@transaction.atomic
def transfer_reader(reader_id, reader_room):
    reader = Reader.objects.select_for_update().get(pk=reader_id)
    history = get_active_reader_history(reader)

    if history is None:
        raise ValidationError("Читатель не записан в библиотеку")

    if history.reader_room_id == reader_room.id:
        raise ValidationError("Читатель уже закреплён за этим залом")

    today = timezone.localdate()

    history.end_date = today
    history.save(update_fields=['end_date'])

    return ReaderRoomHistory.objects.create(
        reader=reader,
        reader_room=reader_room,
        start_date=today,
        reason=ReaderRoomHistory.Reason.TRANSFER
    )


@transaction.atomic
def reregister_reader(reader_id, library_card_number=None):
    reader = Reader.objects.select_for_update().get(pk=reader_id)

    if get_active_reader_history(reader) is None:
        raise ValidationError("Читатель не записан в библиотеку")

    if library_card_number is not None:
        if Reader.objects.exclude(pk=reader.pk).filter(
            library_card_number=library_card_number
        ).exists():
            raise ValidationError("Номер билета уже используется")

        reader.library_card_number = library_card_number

    reader.last_registration_date = timezone.localdate()
    reader.save(update_fields=[
        'last_registration_date',
        'library_card_number'
    ])

    return reader


def one_year_ago(today):
    try:
        return today.replace(year=today.year - 1)
    except ValueError:
        return today.replace(
            year=today.year - 1,
            day=28
        )


@transaction.atomic
def expel_expired_readers():
    today = timezone.localdate()
    cutoff = one_year_ago(today)

    readers = Reader.objects.select_for_update().filter(
        last_registration_date__lt=cutoff
    ).order_by('pk')

    count = 0

    for reader in readers:
        history = get_active_reader_history(reader)

        if history is not None:
            history.end_date = today
            history.save(update_fields=['end_date'])
            count += 1

    return count



# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------



def get_active_book_history(book_copy):
    return BookCopyRoomHistory.objects.filter(
        book_copy=book_copy,
        end_date__isnull=True
    ).first()


@transaction.atomic
def accept_book_copy(book, reader_room):
    book_copy = BookCopy.objects.create(book=book)

    BookCopyRoomHistory.objects.create(
        book_copy=book_copy,
        reader_room=reader_room,
        start_date=timezone.localdate()
    )

    return book_copy


@transaction.atomic
def scrap_book_copy(book_copy_id):
    book_copy = BookCopy.objects.select_for_update().get(
        pk=book_copy_id
    )

    if book_copy.scrapped_at is not None:
        raise ValidationError("Экземпляр уже списан")

    history = get_active_book_history(book_copy)

    if history is None:
        raise ValidationError("Экземпляр не закреплён за залом")

    today = timezone.localdate()

    book_copy.scrapped_at = today
    book_copy.save(update_fields=['scrapped_at'])

    history.end_date = today
    history.save(update_fields=['end_date'])

    return book_copy


@transaction.atomic
def transfer_book_copy(book_copy_id, reader_room):
    book_copy = BookCopy.objects.select_for_update().get(
        pk=book_copy_id
    )

    if book_copy.scrapped_at is not None:
        raise ValidationError("Экземпляр списан")

    history = get_active_book_history(book_copy)

    if history is None:
        raise ValidationError("Экземпляр не закреплён за залом")

    if history.reader_room_id == reader_room.id:
        raise ValidationError("Экземпляр уже находится в этом зале")

    today = timezone.localdate()

    history.end_date = today
    history.save(update_fields=['end_date'])

    return BookCopyRoomHistory.objects.create(
        book_copy=book_copy,
        reader_room=reader_room,
        start_date=today
    )



# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------



@transaction.atomic
def issue_book(reader, book_copy):
    reader = Reader.objects.select_for_update().get(
        pk=reader.pk
    )

    book_copy = BookCopy.objects.select_for_update().get(
        pk=book_copy.pk
    )

    if get_active_reader_history(reader) is None:
        raise ValidationError("Читатель не записан в библиотеку")

    if book_copy.scrapped_at is not None:
        raise ValidationError("Экземпляр списан")

    if get_active_book_history(book_copy) is None:
        raise ValidationError("Экземпляр не закреплён за залом")

    if Loan.objects.filter(
        book_copy=book_copy,
        return_date__isnull=True
    ).exists():
        raise ValidationError("Экземпляр уже выдан")

    return Loan.objects.create(
        reader=reader,
        book_copy=book_copy,
        issued_date=timezone.localdate()
    )


@transaction.atomic
def return_book(loan_id):
    loan = Loan.objects.select_for_update().get(pk=loan_id)

    if loan.return_date is not None:
        raise ValidationError("Книга уже возвращена")

    loan.return_date = timezone.localdate()
    loan.save(update_fields=['return_date'])

    return loan