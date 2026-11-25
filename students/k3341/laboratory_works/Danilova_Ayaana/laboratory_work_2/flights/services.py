from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from datetime import date

from django.db import transaction

from .models import Flight, Passenger, Passport, Reservation, Review, Ticket, User


class ReservationServiceError(Exception):
    """Базовое бизнес-исключение сервисного слоя бронирования."""


class FlightFullError(ReservationServiceError):
    """Выбрасывается, когда на рейсе недостаточно свободных мест (HTTP 409 Conflict)."""


def _parse_uuid_list(raw_ids: Sequence[str | uuid.UUID]) -> list[uuid.UUID]:
    """Безопасно преобразует список строк из POST-запроса в список объектов UUID."""
    result: list[uuid.UUID] = []
    for raw_id in raw_ids:
        try:
            uid = raw_id if isinstance(raw_id, uuid.UUID) else uuid.UUID(str(raw_id))
        except (ValueError, TypeError) as exc:
            raise ReservationServiceError("Передан некорректный идентификатор пассажира.") from exc
        if uid not in result:
            result.append(uid)
    return result


@transaction.atomic
def create_passenger(
    *,
    owner: User,
    first_name: str,
    last_name: str,
    birth_date: date,
    passport_number: str,
) -> Passenger:
    """Атомарно создает профиль пассажира (члена семьи) и привязывает к нему активный паспорт."""
    passenger = Passenger.objects.create(
        owner=owner,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
    )
    Passport.objects.create(
        passenger=passenger,
        passport_number=passport_number,
        is_active=True,
    )
    return passenger


@transaction.atomic
def create_reservation(
    *,
    purchaser: User,
    flight_id: uuid.UUID,
    passenger_ids: Sequence[str | uuid.UUID],
) -> Reservation:
    """
    Атомарно создает резервирование и билеты для выбранных членов семьи.
    Использует пессимистичную блокировку (select_for_update) строки рейса
    для защиты от состояния гонки (Race Condition / овербукинга).
    """
    clean_passenger_ids = _parse_uuid_list(passenger_ids)
    if not clean_passenger_ids:
        raise ReservationServiceError("Выберите хотя бы одного пассажира для бронирования.")

    try:
        flight = Flight.objects.select_for_update().get(pk=flight_id)
    except Flight.DoesNotExist as exc:
        raise ReservationServiceError("Рейс не найден.") from exc

    passengers = list(
        Passenger.objects.filter(
            id__in=clean_passenger_ids,
            owner=purchaser,
            passports__is_active=True,
        ).distinct()
    )
    if len(passengers) != len(clean_passenger_ids):
        raise ReservationServiceError(
            "Некоторые из выбранных пассажиров не найдены или не имеют активного паспорта."
        )

    already_booked = Ticket.objects.filter(
        flight=flight,
        passenger_id__in=clean_passenger_ids,
    ).exists()
    if already_booked:
        raise ReservationServiceError(
            "Один или несколько выбранных пассажиров уже имеют билет на этот рейс."
        )

    occupied_seats: set[int] = set(
        Ticket.objects.filter(flight=flight).values_list("seat_number", flat=True)
    )
    available_seats: list[int] = [
        seat for seat in range(1, flight.capacity + 1) if seat not in occupied_seats
    ]

    if len(available_seats) < len(passengers):
        raise FlightFullError(
            f"Недостаточно свободных мест на рейсе. Доступно: {len(available_seats)}, "
            f"выбрано пассажиров: {len(passengers)}."
        )

    reservation = Reservation.objects.create(
        purchaser=purchaser,
        flight=flight,
    )

    tickets_to_create: list[Ticket] = [
        Ticket(
            reservation=reservation,
            flight=flight,
            passenger=passenger,
            seat_number=available_seats[idx],
        )
        for idx, passenger in enumerate(passengers)
    ]
    Ticket.objects.bulk_create(tickets_to_create)

    return reservation


@transaction.atomic
def update_reservation_tickets(
    *,
    reservation: Reservation,
    seat_updates: Mapping[uuid.UUID, int],
    tickets_to_delete: set[uuid.UUID],
) -> bool:
    """
    Атомарно обновляет номера мест и удаляет отмеченные билеты внутри брони.
    Возвращает True, если бронь сохранена, или False, если были удалены все билеты (и сама бронь).
    """
    flight = Flight.objects.select_for_update().get(pk=reservation.flight_id)
    tickets = list(reservation.tickets.all())

    for ticket in tickets:
        if ticket.pk in tickets_to_delete:
            ticket.delete()
            continue

        if ticket.pk in seat_updates:
            new_seat = seat_updates[ticket.pk]
            if not (1 <= new_seat <= flight.capacity):
                raise ReservationServiceError(
                    f"Номер места должен быть в диапазоне от 1 до {flight.capacity}."
                )
            if ticket.seat_number != new_seat:
                ticket.seat_number = new_seat
                ticket.save(update_fields=["seat_number"])

    if not reservation.tickets.exists():
        reservation.delete()
        return False

    return True


@transaction.atomic
def delete_reservation(*, reservation: Reservation) -> None:
    """
    Безопасно удаляет резервирование вместе со всеми связанными билетами
    (соблюдая ограничение on_delete=models.PROTECT на модели Ticket).
    """
    reservation.tickets.all().delete()
    reservation.delete()


@transaction.atomic
def create_review(
    *,
    author: User,
    flight: Flight,
    rating: int,
    text: str,
    flight_date: date | None = None,
) -> Review:
    """Создает отзыв пользователя о рейсе."""
    return Review.objects.create(
        author=author,
        flight=flight,
        rating=rating,
        text=text,
        flight_date=flight_date,
    )