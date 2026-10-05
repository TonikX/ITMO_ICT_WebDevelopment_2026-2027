from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReservationForm, ReviewForm, UserRegisterForm
from .models import Reservation, Tour


def tour_list(request):
    query = request.GET.get("q", "").strip()
    country = request.GET.get("country", "").strip()
    tours = Tour.objects.all()
    countries = Tour.objects.order_by("country").values_list("country", flat=True).distinct()

    if query:
        tours = tours.filter(
            Q(name__icontains=query)
            | Q(agency__icontains=query)
            | Q(country__icontains=query)
        )

    if country:
        tours = tours.filter(country=country)

    paginator = Paginator(tours, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "library/tour_list.html",
        {
            "page_obj": page_obj,
            "query": query,
            "country": country,
            "countries": countries,
        },
    )


def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    return render(request, "library/tour_detail.html", {"tour": tour})


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tour_list")
    else:
        form = UserRegisterForm()

    return render(request, "library/form.html", {"form": form, "title": "Регистрация"})


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("tour_list")
    else:
        form = AuthenticationForm()

    return render(request, "library/form.html", {"form": form, "title": "Вход"})


def logout_user(request):
    logout(request)
    return redirect("tour_list")


@login_required
def reserve_tour(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.tour = tour
            reservation.save()
            return redirect("my_reservations")
    else:
        form = ReservationForm()

    return render(
        request,
        "library/form.html",
        {
            "form": form,
            "title": f"Забронировать тур: {tour.name}",
        },
    )


@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).select_related("tour")
    return render(request, "library/my_reservations.html", {"reservations": reservations})


@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == "POST":
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            updated_reservation = form.save(commit=False)
            updated_reservation.is_confirmed = False
            updated_reservation.save()
            return redirect("my_reservations")
    else:
        form = ReservationForm(instance=reservation)

    return render(request, "library/form.html", {"form": form, "title": "Редактировать бронирование"})


@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == "POST":
        reservation.delete()
        return redirect("my_reservations")

    return render(request, "library/reservation_confirm_delete.html", {"reservation": reservation})


@login_required
def add_review(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.tour = tour
            review.user = request.user
            review.tour_start_date = tour.start_date
            review.tour_end_date = tour.end_date
            review.save()
            return redirect("tour_detail", tour_id=tour.id)
    else:
        form = ReviewForm()

    return render(request, "library/form.html", {"form": form, "title": f"Отзыв о туре: {tour.name}"})


def sold_by_country(request):
    rows = (
        Reservation.objects.filter(is_confirmed=True)
        .values("tour__country")
        .annotate(
            reservations_count=Count("id"),
            tourists_count=Sum("tourists_count"),
        )
        .order_by("tour__country")
    )

    return render(request, "library/sold_by_country.html", {"rows": rows})


@login_required
def admin_reservations(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect("tour_list")

    reservations = Reservation.objects.select_related("tour", "user")
    return render(request, "library/admin_reservations.html", {"reservations": reservations})


@login_required
def confirm_reservation(request, reservation_id):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect("tour_list")

    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == "POST":
        reservation.is_confirmed = True
        reservation.save()

    return redirect("admin_reservations")
