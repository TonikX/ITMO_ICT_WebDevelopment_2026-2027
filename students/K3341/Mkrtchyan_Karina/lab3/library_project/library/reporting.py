from calendar import monthrange
from datetime import date, datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone

from . import models


def months_before(day, months):
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, min(day.day, monthrange(year, month + 1)[1]))


def active_readers(day):
    return models.Reader.objects.filter(registered_at__lte=day).filter(
        Q(deregistered_at__isnull=True) | Q(deregistered_at__gt=day),)


def midnight(day):
    return timezone.make_aware(datetime.combine(day, time.min))


def monthly_report(start):
    days = monthrange(start.year, start.month)[1]  # число дней в данном месяце
    stop = start + timedelta(days=days)  # первое число следующего месяца

    # список залов, сортируем по pk
    rooms = list(models.ReadingRoom.objects.order_by('pk').values('id_room', 'room_number', 'name'))

    # история размещения экземпляров за месяц
    # - размещение началось раньше stop и закончилось позже start, либо еще не закончилось
    placements = list(models.CopyRoomHistory.objects.filter(valid_from__lt=midnight(stop)).filter(
        Q(valid_to__isnull=True) | Q(valid_to__gt=midnight(start)),).values_list('room_id', 'copy_id', 'valid_from', 'valid_to'))

    # история изменения закрепления читателей за залами за месяц (читатель прикреплен и зарегистрирован раньше stop)
    assignments = list(models.ReaderRoomHistory.objects.filter(
        valid_from__lt=stop, reader__registered_at__lt=stop,).filter(Q(valid_to__isnull=True) | Q(valid_to__gt=start)).values_list(
        'room_id', 'reader_id', 'valid_from', 'valid_to',))

    # активные читатели на момент месяца
    readers = list(models.Reader.objects.filter(registered_at__lt=stop).filter(
        Q(deregistered_at__isnull=True) | Q(deregistered_at__gt=start),).values_list('pk', 'registered_at', 'deregistered_at'))

    # новые читатели, которые зарегистрировались в этом месяце
    new_readers = models.Reader.objects.filter(registered_at__gte=start, registered_at__lt=stop)

    first_rooms = {}  # для каждого нового читателя сохраняем {id читателя: id его первого зала}.
    for reader_id, room_id in models.ReaderRoomHistory.objects.filter(reader__in=new_readers).order_by(
        'reader_id', 'valid_from', 'pk',
    ).values_list('reader_id', 'room_id'):
        first_rooms.setdefault(reader_id, room_id)  # номер зала не меняется для читателя

    # считаем число новых читателей по залам
    registrations = {room['id_room']: 0 for room in rooms}
    for room_id in first_rooms.values():
        registrations[room_id] += 1


    daily = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        at = midnight(day + timedelta(days=1)) - timedelta(microseconds=1)  # последний момент дня
        # активные читатели на момент дня
        registered = {pk for pk, since, until in readers if since <= day and (until is None or day < until)}

        # история размещения читателей и экземпляров за день
        room_copies = {pk: set() for pk in registrations}
        room_readers = {pk: set() for pk in registrations}
        for room_id, copy_id, since, until in placements:
            if since <= at and (until is None or at < until):
                room_copies[room_id].add(copy_id)
        for room_id, reader_id, since, until in assignments:
            if reader_id in registered and since <= day and (until is None or day < until):
                room_readers[room_id].add(reader_id)
        daily.append({
            'date': day, 'copy_count': len(set().union(*room_copies.values())),
            'reader_count': len(registered),
            'rooms': [dict(room, copy_count=len(room_copies[room['id_room']]),
                           reader_count=len(room_readers[room['id_room']])) for room in rooms],
        })

    # результат отчета - словарь: выбранный месяц, отчеты по дням,
    # число новых читателей и распределение их числа по первым закрепленным за ними залам
    return {
        'month': start.strftime('%Y-%m'), 'days': daily,
        'registrations': {'reader_count': new_readers.count(), 'rooms': [
            dict(room, reader_count=registrations[room['id_room']]) for room in rooms
        ]},
    }
