from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import CheckInForm, FlightFilterForm, ReservationForm, ReviewForm, SignUpForm, StaffReservationForm
from .models import Flight, Reservation, Review


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@require_http_methods(["GET", "POST"])
def signup(request):
    form = SignUpForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("flights:list")
    return render(request, "form.html", {"form": form, "title": "Регистрация", "submit": "Создать аккаунт"})


def flight_list(request):
    form = FlightFilterForm(request.GET)
    flights = Flight.objects.annotate(reserved_count=Count("reservations")).order_by("departure_at", "pk")
    if form.is_valid():
        query = form.cleaned_data["q"]
        if query:
            flights = flights.filter(Q(number__icontains=query) | Q(airline__icontains=query) |
                                     Q(origin__icontains=query) | Q(destination__icontains=query))
        if form.cleaned_data["direction"]:
            flights = flights.filter(direction=form.cleaned_data["direction"])
        if form.cleaned_data["date"]:
            flights = flights.filter(departure_at__date=form.cleaned_data["date"])
    else:
        flights = flights.none()
    page = Paginator(flights, 8).get_page(request.GET.get("page"))
    return render(request, "flight_list.html", {"page": page, "filter_form": form})


def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, "flight_detail.html", {
        "flight": flight, "free_seats": flight.seat_count - flight.reservations.count(),
        "reviews": flight.reviews.select_related("user"),
    })


@login_required
def passenger_list(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    return render(request, "passengers.html", {
        "flight": flight, "reservations": flight.reservations.select_related("user"),
    })


@login_required
def my_reservations(request):
    reservations = request.user.reservations.select_related("flight")
    return render(request, "my_reservations.html", {"reservations": reservations})


def save_reservation(form):
    flight = form.cleaned_data["flight"]
    flight = Flight.objects.select_for_update().get(pk=flight.pk)
    reservation = form.save(commit=False)
    reservation.flight = flight
    try:
        with transaction.atomic():
            reservation.full_clean()
            reservation.save()
    except ValidationError as error:
        form.add_error(None, error)
        return False
    except IntegrityError:
        form.add_error(None, "Место уже занято. Выберите другое место.")
        return False
    return True


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def reservation_create(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    reservation = Reservation(user=request.user)
    form = ReservationForm(request.POST if request.method == "POST" else None, instance=reservation,
                           initial={"flight": flight, "passenger_name": request.user.get_full_name()})
    if request.method == "POST" and form.is_valid() and save_reservation(form):
        messages.success(request, "Место забронировано.")
        return redirect("flights:my_reservations")
    return render(request, "form.html", {"form": form, "title": "Бронирование места", "submit": "Забронировать"})


@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def reservation_update(request, pk):
    reservation = get_object_or_404(Reservation.objects.select_for_update(), pk=pk, user=request.user)
    form = ReservationForm(request.POST if request.method == "POST" else None, instance=reservation)
    if request.method == "POST" and form.is_valid():
        if form.has_changed():
            form.instance.checked_in = False
            form.instance.ticket_number = None
        if save_reservation(form):
            messages.success(request, "Бронирование обновлено. При изменении данных регистрация на рейс сбрасывается.")
            return redirect("flights:my_reservations")
    return render(request, "form.html", {"form": form, "title": "Редактирование бронирования", "submit": "Сохранить"})


@login_required
@require_http_methods(["GET", "POST"])
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Бронирование удалено.")
        return redirect("flights:my_reservations")
    return render(request, "reservation_confirm_delete.html", {"reservation": reservation})


@staff_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def check_in(request, pk):
    reservation = get_object_or_404(Reservation.objects.select_for_update(), pk=pk)
    form = CheckInForm(request.POST if request.method == "POST" else None, instance=reservation)
    if request.method == "POST" and form.is_valid():
        reservation.checked_in = True
        try:
            with transaction.atomic():
                reservation.save(update_fields=["ticket_number", "checked_in"])
        except IntegrityError:
            form.add_error("ticket_number", "Этот номер билета уже используется.")
        else:
            messages.success(request, "Пассажир зарегистрирован на рейс.")
            return redirect("flights:passengers", pk=reservation.flight_id)
    return render(request, "form.html", {"form": form, "title": f"Регистрация: {reservation.passenger_name}", "submit": "Зарегистрировать"})


@staff_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def staff_reservation_create(request, pk):
    flight = get_object_or_404(Flight.objects.select_for_update(), pk=pk)
    reservation = Reservation(flight=flight, checked_in=True)
    form = StaffReservationForm(request.POST if request.method == "POST" else None, instance=reservation)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(None, "Место или номер билета уже используется. Проверьте данные.")
        else:
            return redirect("flights:passengers", pk=flight.pk)
    return render(request, "form.html", {"form": form, "title": f"Добавление пассажира на {flight.number}", "submit": "Зарегистрировать"})


@login_required
@require_http_methods(["GET", "POST"])
def review_create(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    review = Review(flight=flight, user=request.user, flight_date=timezone.localdate(flight.departure_at))
    form = ReviewForm(request.POST if request.method == "POST" else None, instance=review)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("flights:detail", pk=flight.pk)
    return render(request, "form.html", {"form": form, "title": f"Отзыв о рейсе {flight.number}", "submit": "Опубликовать"})
