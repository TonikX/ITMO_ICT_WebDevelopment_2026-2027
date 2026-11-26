from __future__ import annotations

import uuid
from typing import Any

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, DetailView, ListView, View

from . import selectors, services
from .forms import (
    NewPassengerInlineForm,
    ReviewForm,
    StaffTicketCheckInForm,
    UserCreationForm,
)
from .models import Flight, FlightType, Reservation, Ticket, User
from .services import FlightFullError, ReservationServiceError


def get_safe_next_url(request: HttpRequest, fallback: str) -> str:
    """Проверяет параметр next на защиту от уязвимости Open Redirect."""
    next_url: str | None = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return fallback


def sign_up(request: HttpRequest) -> HttpResponse:
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect("flights:flight_list")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("flights:flight_list")
    else:
        form = UserCreationForm()

    return render(request, "registration/sign_up.html", {"form": form})


class FlightListView(ListView):
    """Список всех рейсов с пагинацией, поиском и фильтрацией через селектор."""
    model = Flight
    template_name = "flights/flight_list.html"
    context_object_name = "flights"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Flight]:
        return selectors.flight_list(
            airline_query=self.request.GET.get("airline", "").strip() or None,
            search_query=self.request.GET.get("q", "").strip() or None,
            flight_type=self.request.GET.get("flight_type", "").strip() or None,
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["flight_types"] = FlightType.choices
        context["current_airline"] = self.request.GET.get("airline", "")
        context["current_q"] = self.request.GET.get("q", "")
        context["current_type"] = self.request.GET.get("flight_type", "")
        return context


class FlightDetailView(DetailView):
    """Детальная страница рейса: информация, таблица пассажиров и отзывы."""

    model = Flight
    template_name = "flights/flight_detail.html"
    context_object_name = "flight"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        flight: Flight = self.object
        user = self.request.user

        # Все билеты на рейс для точного подсчёта свободных мест
        all_tickets = list(selectors.flight_tickets_with_passengers(flight=flight))
        seats_taken = len(all_tickets)
        seats_available = max(0, flight.capacity - seats_taken)

        if user.is_authenticated and user.is_staff:
            visible_tickets = all_tickets
            for ticket in visible_tickets:
                ticket.staff_form = StaffTicketCheckInForm(instance=ticket)  # type: ignore[attr-defined]
        elif user.is_authenticated:
            visible_tickets = [
                t
                for t in all_tickets
                if t.passenger.owner_id == user.id or t.reservation.purchaser_id == user.id
            ]
        else:
            visible_tickets = []

        context["tickets"] = visible_tickets
        context["user_tickets_count"] = len(visible_tickets)
        context["seats_taken"] = seats_taken
        context["seats_available"] = seats_available
        context["reviews"] = selectors.flight_reviews(flight=flight)
        context["review_form"] = ReviewForm()

        if user.is_authenticated and isinstance(user, User):
            context["user_reservation"] = selectors.user_reservation_for_flight(
                user=user,
                flight=flight,
            )
        else:
            context["user_reservation"] = None

        return context


class ReservationListView(LoginRequiredMixin, ListView):
    """Список резервирований текущего пользователя с пагинацией."""
    model = Reservation
    template_name = "flights/reservation_list.html"
    context_object_name = "reservations"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Reservation]:
        return selectors.reservations_for_user(
            purchaser=self.request.user  # type: ignore[arg-type]
        )


@login_required
def passenger_create(request: HttpRequest) -> HttpResponse:
    """Добавление нового пассажира (члена семьи) и его паспорта через сервис."""
    fallback_url: str = reverse("flights:reservation_list")
    next_url: str = get_safe_next_url(request, fallback=fallback_url)

    if request.method == "POST":
        form = NewPassengerInlineForm(request.POST)
        if form.is_valid():
            try:
                services.create_passenger(
                    owner=request.user,  # type: ignore[arg-type]
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    birth_date=form.cleaned_data["birth_date"],
                    passport_number=form.cleaned_data["passport_number"],
                )
            except IntegrityError:
                form.add_error("passport_number", "Паспорт с таким номером уже зарегистрирован.")
            except Exception as exc:
                form.add_error(None, f"Произошла ошибка при сохранении пассажира: {exc}")
            else:
                return redirect(next_url)
    else:
        form = NewPassengerInlineForm()

    return render(request, "flights/passenger_form.html", {"form": form, "next": next_url})


@login_required
def reservation_create(request: HttpRequest, flight_id: uuid.UUID) -> HttpResponse:
    """Создание резервирования на рейс для выбранных пассажиров."""
    flight: Flight = get_object_or_404(Flight, pk=flight_id)
    fallback_url: str = reverse("flights:reservation_list")
    next_url: str = get_safe_next_url(request, fallback=fallback_url)

    if request.method == "POST":
        try:
            services.create_reservation(
                purchaser=request.user,  # type: ignore[arg-type]
                flight_id=flight.pk,
                passenger_ids=request.POST.getlist("passengers"),
            )
        except ReservationServiceError as exc:
            passengers = selectors.available_passengers(
                owner=request.user,  # type: ignore[arg-type]
                flight=flight,
            )
            return render(
                request,
                "flights/reservation_form.html",
                {"flight": flight, "passengers": passengers, "error": str(exc), "next": next_url},
                status=409 if isinstance(exc, FlightFullError) else 400,
            )
        except IntegrityError:
            passengers = selectors.available_passengers(
                owner=request.user,  # type: ignore[arg-type]
                flight=flight,
            )
            return render(
                request,
                "flights/reservation_form.html",
                {
                    "flight": flight,
                    "passengers": passengers,
                    "error": "Бронирование изменилось параллельно. Обновите страницу и попробуйте снова.",
                    "next": next_url,
                },
                status=409,
            )
        return redirect(next_url)

    passengers = selectors.available_passengers(
        owner=request.user,  # type: ignore[arg-type]
        flight=flight,
    )
    return render(
        request,
        "flights/reservation_form.html",
        {"flight": flight, "passengers": passengers, "next": next_url},
    )


class ReservationUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Редактирование резервирования пользователем (смена мест или удаление билетов)."""
    template_name = "flights/reservation_update.html"

    def get_object(self) -> Reservation:
        return selectors.get_reservation_with_tickets(reservation_id=self.kwargs["pk"])

    def test_func(self) -> bool:
        reservation = self.get_object()
        return reservation.purchaser_id == self.request.user.pk or self.request.user.is_staff

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        reservation = self.get_object()
        return render(
            request,
            self.template_name,
            {"reservation": reservation, "tickets": reservation.tickets.all()},
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        reservation = self.get_object()
        tickets = list(reservation.tickets.all())

        seat_updates: dict[uuid.UUID, int] = {}
        tickets_to_delete: set[uuid.UUID] = set()

        try:
            for ticket in tickets:
                if request.POST.get(f"delete_ticket_{ticket.pk}"):
                    tickets_to_delete.add(ticket.pk)
                    continue

                raw_seat = request.POST.get(f"seat_{ticket.pk}")
                if raw_seat:
                    try:
                        seat_updates[ticket.pk] = int(raw_seat)
                    except ValueError as exc:
                        raise ReservationServiceError("Номер места должен быть целым числом.") from exc

            services.update_reservation_tickets(
                reservation=reservation,
                seat_updates=seat_updates,
                tickets_to_delete=tickets_to_delete,
            )
        except ReservationServiceError as exc:
            return render(
                request,
                self.template_name,
                {"reservation": reservation, "tickets": reservation.tickets.all(), "error": str(exc)},
                status=400,
            )
        except IntegrityError:
            return render(
                request,
                self.template_name,
                {
                    "reservation": reservation,
                    "tickets": reservation.tickets.all(),
                    "error": "Выбранное место уже занято другим пассажиром на этом рейсе.",
                },
                status=409,
            )

        return redirect("flights:reservation_list")


class ReservationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление резервирования через сервисный слой."""
    model = Reservation
    template_name = "flights/reservation_confirm_delete.html"
    success_url = reverse_lazy("flights:reservation_list")

    def get_object(self, queryset: QuerySet[Reservation] | None = None) -> Reservation:
        return selectors.get_reservation_with_tickets(reservation_id=self.kwargs["pk"])

    def test_func(self) -> bool:
        reservation = self.get_object()
        return reservation.purchaser_id == self.request.user.pk or self.request.user.is_staff

    def form_valid(self, form: Any) -> HttpResponse:
        services.delete_reservation(reservation=self.get_object())
        return redirect(self.get_success_url())


@login_required
@require_POST
def review_create(request: HttpRequest, flight_id: uuid.UUID) -> HttpResponse:
    """Создание отзыва к рейсу через сервисный слой."""
    flight: Flight = get_object_or_404(Flight, pk=flight_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        services.create_review(
            author=request.user,  # type: ignore[arg-type]
            flight=flight,
            rating=form.cleaned_data["rating"],
            text=form.cleaned_data["text"],
            flight_date=form.cleaned_data.get("flight_date"),
        )
        messages.success(request, "Ваш отзыв успешно опубликован!")
    else:
        messages.error(request, "Ошибка в форме отзыва. Проверьте оценку (от 1 до 10).")

    return redirect("flights:flight_detail", pk=flight.pk)


@login_required
@require_POST
def staff_ticket_checkin(request: HttpRequest, ticket_id: uuid.UUID) -> HttpResponse:
    """
    Клиентское действие сотрудника аэропорта (is_staff):
    регистрация пассажира на рейс и ввод номера билета прямо из таблицы рейса.
    """
    if not request.user.is_staff:
        raise PermissionDenied("Только сотрудники аэропорта могут регистрировать пассажиров на рейс.")

    ticket: Ticket = get_object_or_404(Ticket, pk=ticket_id)
    form = StaffTicketCheckInForm(request.POST, instance=ticket)
    if form.is_valid():
        form.save()
        messages.success(request, f"Данные билета пассажира {ticket.passenger} успешно обновлены.")
    else:
        messages.error(request, "Ошибка при обновлении билета. Проверьте номер места и билета.")

    return redirect("flights:flight_detail", pk=ticket.flight_id)