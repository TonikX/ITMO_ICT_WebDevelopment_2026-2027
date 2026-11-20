from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import BookingForm, RegistrationForm, ReviewForm
from .models import Booking, Country, Review, Tour


def tour_list(request):
    query = request.GET.get("q", "").strip()
    country = request.GET.get("country", "")
    tours = Tour.objects.select_related("country", "agency")
    if query:
        tours = tours.filter(Q(title__icontains=query) | Q(description__icontains=query)
                             | Q(agency__name__icontains=query))
    if country.isdigit():
        tours = tours.filter(country_id=country)
    page = Paginator(tours, 6).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "tour_list.html", {
        "page": page, "countries": Country.objects.all(), "query": query,
        "selected_country": country, "filter_query": params.urlencode(),
    })


def tour_detail(request, pk):
    tour = get_object_or_404(Tour.objects.select_related("country", "agency"), pk=pk)
    booking = None
    if request.user.is_authenticated:
        booking = Booking.objects.filter(user=request.user, tour=tour).first()
    return render(request, "tour_detail.html", {
        "tour": tour, "booking": booking,
        "reviews": tour.reviews.select_related("user"), "review_form": ReviewForm(),
        "can_book": tour.start_date >= timezone.localdate(),
    })


def register(request):
    if request.user.is_authenticated:
        return redirect("tour_list")
    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Вы зарегистрированы. Теперь можно забронировать тур.")
        return redirect("tour_list")
    return render(request, "form.html", {"form": form, "title": "Регистрация", "button": "Зарегистрироваться"})


@login_required
def booking_create(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    existing = Booking.objects.filter(tour=tour, user=request.user).first()
    if existing:
        return redirect("booking_edit", pk=existing.pk)
    booking = Booking(user=request.user, tour=tour, unit_price=tour.price)
    form = BookingForm(request.POST if request.method == "POST" else None, instance=booking)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error(None, "У вас уже есть бронирование этого тура.")
        else:
            messages.success(request, "Бронирование отправлено. Дождитесь подтверждения.")
            return redirect("my_bookings")
    return render(request, "form.html", {
        "form": form, "title": f"Бронирование: {tour.title}", "button": "Забронировать",
        "note": f"Цена за человека: {tour.price:,.0f} ₽. {tour.payment_terms}",
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("tour", "tour__country")
    return render(request, "my_bookings.html", {"bookings": bookings})


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("tour"), pk=pk, user=request.user)
    form = BookingForm(request.POST if request.method == "POST" else None, instance=booking)
    if request.method == "POST" and form.is_valid():
        booking = form.save(commit=False)
        booking.status = Booking.Status.PENDING
        booking.save()
        messages.success(request, "Изменения сохранены. Бронирование отправлено на повторное подтверждение.")
        return redirect("my_bookings")
    return render(request, "form.html", {
        "form": form, "title": f"Изменить бронирование: {booking.tour.title}",
        "button": "Сохранить", "note": "После изменения администратор подтвердит бронирование заново.",
    })


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("tour"), pk=pk, user=request.user)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Бронирование удалено.")
        return redirect("my_bookings")
    return render(request, "booking_delete.html", {"booking": booking})


@login_required
@require_POST
def review_create(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    review = Review(user=request.user, tour=tour, start_date=tour.start_date, end_date=tour.end_date)
    form = ReviewForm(request.POST, instance=review)
    if form.is_valid():
        form.save()
        messages.success(request, "Отзыв добавлен.")
        return redirect("tour_detail", pk=tour.pk)
    return render(request, "tour_detail.html", {
        "tour": tour, "reviews": tour.reviews.select_related("user"), "review_form": form,
        "booking": Booking.objects.filter(user=request.user, tour=tour).first(),
        "can_book": tour.start_date >= timezone.localdate(),
    })


def sales(request):
    amount = ExpressionWrapper(F("unit_price") * F("travelers"),
                               output_field=DecimalField(max_digits=14, decimal_places=2))
    sold = Booking.objects.filter(status=Booking.Status.CONFIRMED)
    countries = sold.values("tour__country__name").annotate(
        bookings_count=Count("id"), travelers_count=Sum("travelers"), total=Sum(amount),
    ).order_by("tour__country__name")
    tours = sold.values("tour_id", "tour__title", "tour__country__name", "tour__start_date", "tour__end_date").annotate(
        bookings_count=Count("id"), travelers_count=Sum("travelers"), total=Sum(amount),
    ).order_by("tour__country__name", "tour__start_date", "tour_id")
    return render(request, "sales.html", {"countries": countries, "sold_tours": tours})


def is_manager(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_manager)
def booking_manage(request):
    bookings = Booking.objects.select_related("tour", "user", "tour__country").order_by("status", "-created_at")
    return render(request, "booking_manage.html", {"bookings": bookings})


@user_passes_test(is_manager)
@require_POST
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    booking.status = Booking.Status.CONFIRMED
    booking.save(update_fields=["status"])
    messages.success(request, "Бронирование подтверждено.")
    return redirect("booking_manage")
