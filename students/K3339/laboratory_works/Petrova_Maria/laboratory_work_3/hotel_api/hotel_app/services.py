from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Accommodation, Employee, Floor, Guest, Room, Stay


def quarterly_report(year, quarter):
    month = (quarter - 1) * 3 + 1
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if quarter == 4 else date(year, month + 3, 1)
    accommodations = overlapping_accommodations(start, end).prefetch_related("stays")
    revenues = {}
    guests = {}
    for accommodation in accommodations:
        check_out = accommodation.actual_check_out or accommodation.planned_check_out
        nights = (min(check_out, end) - max(accommodation.check_in, start)).days
        room_id = accommodation.room_id
        # Стоимость считаем по заселению, а не по связям с гостями.
        revenues[room_id] = revenues.get(room_id, Decimal("0.00")) + (
            accommodation.price_per_night * nights
        )
        guests.setdefault(room_id, set()).update(
            stay.guest_id for stay in accommodation.stays.all()
        )

    rooms = []
    total = Decimal("0.00")
    for room in Room.objects.order_by("pk"):
        revenue = revenues.get(room.pk, Decimal("0.00"))
        total += revenue
        rooms.append({
            "room_id": room.pk, "room_number": room.number,
            "guest_count": len(guests.get(room.pk, set())),
            "revenue": format(revenue, ".2f"),
        })
    floors = [
        {"floor_id": floor.pk, "floor_number": floor.number, "room_count": floor.room_count}
        for floor in Floor.objects.annotate(room_count=Count("rooms")).order_by("pk")
    ]
    return {
        "year": year, "quarter": quarter, "rooms": rooms, "floors": floors,
        "total_revenue": format(total, ".2f"),
    }


def overlapping_accommodations(start, end):
    return Accommodation.objects.annotate(
        end_date=Coalesce("actual_check_out", "planned_check_out")
    ).filter(check_in__lt=end, end_date__gt=start)


def lock_guests(guest_ids):
    # Единый порядок блокировок: гости по ID, затем номер.
    guests = list(
        Guest.objects.select_for_update().filter(pk__in=guest_ids).order_by("pk")
    )
    if len(guests) != len(guest_ids):
        raise ValidationError({"guests": "Один из гостей больше не существует."})
    return guests


@transaction.atomic
def check_in(room, guests, check_in, planned_check_out):
    guests = lock_guests([guest.pk for guest in guests])
    room = get_object_or_404(Room.objects.select_for_update(), pk=room.pk)
    if len(guests) > room.room_type.capacity:
        raise ValidationError({"error": "Количество гостей превышает вместимость номера."})
    overlaps = overlapping_accommodations(check_in, planned_check_out)
    if overlaps.filter(room=room).exists():
        raise ValidationError({"error": "Номер занят на выбранные даты."})
    if overlaps.filter(stays__guest__in=guests).exists():
        raise ValidationError({"guests": "Один из гостей уже проживает в гостинице в эти даты."})
    accommodation = Accommodation.objects.create(
        room=room,
        check_in=check_in,
        planned_check_out=planned_check_out,
        price_per_night=room.room_type.price_per_night,
    )
    Stay.objects.bulk_create([
        Stay(guest=guest, accommodation=accommodation) for guest in guests
    ])
    return accommodation


@transaction.atomic
def check_out(accommodation_id, actual_check_out):
    accommodation = get_object_or_404(Accommodation, pk=accommodation_id)
    guest_ids = list(accommodation.stays.values_list("guest_id", flat=True))
    lock_guests(guest_ids)
    Room.objects.select_for_update().get(pk=accommodation.room_id)
    accommodation = Accommodation.objects.select_for_update().get(pk=accommodation_id)
    if accommodation.actual_check_out is not None:
        raise ValidationError({"error": "Проживание уже завершено."})
    if actual_check_out <= accommodation.check_in:
        raise ValidationError({"actual_check_out": "Выезд должен быть позже заселения."})
    overlaps = overlapping_accommodations(
        accommodation.check_in, actual_check_out
    ).exclude(pk=accommodation.pk)
    if overlaps.filter(room_id=accommodation.room_id).exists():
        raise ValidationError({"error": "Дата выезда пересекается с другим заселением номера."})
    if overlaps.filter(stays__guest_id__in=guest_ids).exists():
        raise ValidationError({"error": "Дата выезда пересекается с другим проживанием гостя."})
    accommodation.actual_check_out = actual_check_out
    accommodation.save(update_fields=["actual_check_out"])
    return accommodation


@transaction.atomic
def dismiss_employee(employee_id, dismissed_on):
    employee = get_object_or_404(Employee.objects.select_for_update(), pk=employee_id)
    if employee.dismissed_on is not None:
        raise ValidationError({"error": "Сотрудник уже уволен."})
    if dismissed_on < employee.hired_on:
        raise ValidationError({"dismissed_on": "Увольнение не может быть раньше приёма."})
    employee.dismissed_on = dismissed_on
    employee.save(update_fields=["dismissed_on"])
    assignments = employee.cleaning_assignments
    assignments.filter(valid_from__gte=dismissed_on).delete()
    assignments.filter(valid_to__isnull=True).update(valid_to=dismissed_on)
    assignments.filter(valid_to__gt=dismissed_on).update(valid_to=dismissed_on)
    if employee.user_id:
        get_user_model().objects.filter(pk=employee.user_id).update(is_active=False)
    return employee
