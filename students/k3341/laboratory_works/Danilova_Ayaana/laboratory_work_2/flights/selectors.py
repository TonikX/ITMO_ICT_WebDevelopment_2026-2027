from __future__ import annotations

import uuid
from django.db.models import Prefetch, Q, QuerySet
from django.shortcuts import get_object_or_404

from .models import (
    Flight,
    FlightType,
    Passenger,
    Passport,
    Reservation,
    Review,
    Ticket,
    User,
)


def flight_list(
    *,
    airline_query: str | None = None,
    search_query: str | None = None,
    flight_type: str | None = None,
) -> QuerySet[Flight]:
    """Возвращает отфильтрованный список рейсов для главной таблицы."""
    queryset = Flight.objects.all()

    if airline_query:
        queryset = queryset.filter(airline__icontains=airline_query)

    if flight_type in FlightType.values:
        queryset = queryset.filter(flight_type=flight_type)

    if search_query:
        queryset = queryset.filter(
            Q(flight_number__icontains=search_query)
            | Q(airline__icontains=search_query)
            | Q(gate__icontains=search_query)
        )

    return queryset


def flight_reviews(*, flight: Flight) -> QuerySet[Review]:
    """Возвращает все отзывы к рейсу вместе с данными авторов (1 SQL-запрос)."""
    return flight.reviews.select_related("author").all()


def flight_tickets_with_passengers(*, flight: Flight) -> QuerySet[Ticket]:
    """
    Возвращает билеты всех пассажиров рейса, отсортированные по номеру места,
    подтягивая пассажира, бронь и покупателя за 1 SQL-запрос (JOIN).
    """
    return (
        flight.tickets.select_related("passenger", "reservation", "reservation__purchaser")
        .order_by("seat_number")
    )


def user_reservation_for_flight(*, user: User, flight: Flight) -> Reservation | None:
    """Возвращает активную бронь конкретного пользователя на данный рейс (если есть)."""
    return (
        flight.reservations.filter(purchaser=user)
        .prefetch_related(
            Prefetch(
                "tickets",
                queryset=Ticket.objects.select_related("passenger").order_by("seat_number"),
            )
        )
        .first()
    )


def available_passengers(*, owner: User, flight: Flight) -> QuerySet[Passenger]:
    """
    Возвращает сохраненных членов семьи пользователя с активным паспортом,
    которые еще не имеют билета на указанный рейс.
    """
    return (
        Passenger.objects.filter(owner=owner, passports__is_active=True)
        .exclude(tickets__flight=flight)
        .distinct()
        .prefetch_related(
            Prefetch(
                "passports",
                queryset=Passport.objects.filter(is_active=True),
                to_attr="active_passports",
            )
        )
    )


def reservations_for_user(*, purchaser: User) -> QuerySet[Reservation]:
    """Возвращает список всех резервирований пользователя с рейсами и билетами."""
    return (
        Reservation.objects.filter(purchaser=purchaser)
        .select_related("flight")
        .prefetch_related(
            Prefetch(
                "tickets",
                queryset=Ticket.objects.select_related("passenger").order_by("seat_number"),
            )
        )
    )


def get_reservation_with_tickets(*, reservation_id: uuid.UUID) -> Reservation:
    """Возвращает конкретную бронь с предзагруженным рейсом и билетами пассажиров."""
    return get_object_or_404(
        Reservation.objects.select_related("flight").prefetch_related(
            Prefetch(
                "tickets",
                queryset=Ticket.objects.select_related("passenger").order_by("seat_number"),
            )
        ),
        pk=reservation_id,
    )