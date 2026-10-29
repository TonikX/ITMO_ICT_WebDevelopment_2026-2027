from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F, Q
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.views.decorators.cache import never_cache
from .models import Tour, Booking, Review, Country
from .forms import RegistrationForm, BookingForm, ReviewForm


class NordwayLoginView(LoginView):
    template_name = "tours/login.html"

    def get_success_url(self):
        redirect_url = self.get_redirect_url()

        if redirect_url == "/accounts/profile/":
            return reverse("home")

        return redirect_url or reverse("home")
    

def home(request):
    countries = Country.objects.all().order_by("name")

    tours = (
        Tour.objects
        .filter(is_active=True)
        .select_related("country", "company")
    )

    # Поиск по названию тура
    search_query = request.GET.get("q", "").strip()

    if search_query:
            tours = tours.filter(Q(title__icontains=search_query) | Q(country__name__icontains=search_query)
            )

    # Фильтрация по стране
    selected_country = request.GET.get("country", "")

    if selected_country.isdigit():
        country_id = int(selected_country)

        if countries.filter(id=country_id).exists():
            tours = tours.filter(country_id=country_id)
        else:
            selected_country = ""
    else:
        selected_country = ""

    # Сортировка туров
    selected_sort = request.GET.get("sort", "date")

    if selected_sort == "price_asc":
        tours = tours.order_by("price", "start_date")
    elif selected_sort == "price_desc":
        tours = tours.order_by("-price", "start_date")
    else:
        selected_sort = "date"
        tours = tours.order_by("start_date")

    # Пагинация: 6 туров на странице
    paginator = Paginator(tours, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "tours/home.html",
        {
            "tours": page_obj,
            "countries": countries,
            "search_query": search_query,
            "selected_country": selected_country,
            "selected_sort": selected_sort,
        },
    )

def tour_detail(request, pk):
    tour = get_object_or_404(
        Tour.objects.select_related("country", "company").prefetch_related("images"),
        pk=pk,
        is_active=True,
    )

    reviews = (
        Review.objects
        .filter(tour=tour)
        .select_related("user")
        .order_by("-review_date")
    )

    has_review = False

    if request.user.is_authenticated:
        has_review = Review.objects.filter(
            tour=tour,
            user=request.user,
        ).exists()

    review_form = ReviewForm()

    return render(
        request,
        "tours/tour_detail.html",
        {
            "tour": tour,
            "reviews": reviews,
            "has_review": has_review,
            "review_form": review_form,
        },
    )

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()

    return render(request, "tours/register.html", {"form": form})

@login_required
@never_cache
def my_bookings(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .select_related("tour", "tour__country")
    )

    return render(
        request,
        "tours/my_bookings.html",
        {"bookings": bookings},
    )

@login_required
@never_cache
def booking_form(request, pk):
    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            people_count = form.cleaned_data["people_count"]

            with transaction.atomic():
                tour = get_object_or_404(
                    Tour.objects.select_for_update(),
                    pk=pk,
                    is_active=True,
                )

                if people_count > tour.available_places:
                    form.add_error(
                        "people_count",
                        "Недостаточно свободных мест.",
                    )
                else:
                    tour.available_places -= people_count
                    tour.save(update_fields=["available_places"])

                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.tour = tour
                    booking.status = Booking.Status.PENDING
                    booking.save()

                    messages.success(
                        request,
                        "Заявка на бронирование успешно отправлена.",
                    )
                    return redirect("my_bookings")
    else:
        tour = get_object_or_404(
            Tour,
            pk=pk,
            is_active=True,
        )
        form = BookingForm()

    return render(
        request,
        "tours/booking_form.html",
        {"tour": tour, "form": form},
    )

@login_required
@require_POST
def cancel_booking(request, pk):
    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            pk=pk,
            user=request.user,
        )

        if booking.status == Booking.Status.PENDING:
            tour = Tour.objects.select_for_update().get(
                pk=booking.tour_id
            )

            tour.available_places += booking.people_count
            tour.save(update_fields=["available_places"])

            booking.status = Booking.Status.CANCELLED
            booking.save(update_fields=["status"])

            messages.success(
                request,
                "Бронирование отменено.",
            )
        else:
            messages.error(
                request,
                "Отменить можно только заявку со статусом ожидания.",
            )

    return redirect("my_bookings")


@login_required
@never_cache
def edit_booking(request, pk):
    if request.method not in ("GET", "POST"):
        return redirect("my_bookings")

    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            pk=pk,
            user=request.user,
        )

        if booking.status != Booking.Status.PENDING:
            messages.error(
                request,
                "Редактировать можно только заявки со статусом ожидания.",
            )
            return redirect("my_bookings")

        tour = Tour.objects.select_for_update().get(
            pk=booking.tour_id
        )

        # Сохраняем исходное количество до проверки формы
        old_count = booking.people_count

        if request.method == "POST":
            form = BookingForm(request.POST, instance=booking)

            if form.is_valid():
                new_count = form.cleaned_data["people_count"]
                difference = new_count - old_count

                if difference > tour.available_places:
                    form.add_error(
                        "people_count",
                        "Недостаточно свободных мест.",
                    )
                else:
                    tour.available_places -= difference
                    tour.save(
                        update_fields=["available_places"]
                    )

                    form.save()

                    messages.success(
                        request,
                        "Бронирование успешно обновлено.",
                    )
                    return redirect("my_bookings")
        else:
            form = BookingForm(instance=booking)

        return render(
            request,
            "tours/booking_form.html",
            {
                "tour": tour,
                "form": form,
                "is_edit": True,
            },
        )

@login_required
@require_POST
def create_review(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    # Один пользователь может оставить только один отзыв
    # на каждый тур.
    if Review.objects.filter(
        user=request.user,
        tour=tour,
    ).exists():
        messages.error(
            request,
            "Вы уже оставили отзыв об этом туре.",
        )
        return redirect("tour_detail", pk=tour.pk)

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.tour = tour
        review.save()

        messages.success(
            request,
            "Ваш отзыв успешно добавлен.",
        )
    else:
        messages.error(
            request,
            "Проверьте текст отзыва и оценку от 1 до 10.",
        )

    return redirect("tour_detail", pk=tour.pk)


@staff_member_required
def country_statistics(request):
    countries = Country.objects.all().order_by("name")

    statistics = Booking.objects.values(
        "tour__country_id"
    ).annotate(
        total_bookings=Count(
            "id",
            filter=~Q(status=Booking.Status.CANCELLED),
        ),
        confirmed_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.CONFIRMED),
        ),
        revenue=Sum(
            F("people_count") * F("tour__price"),
            filter=Q(status=Booking.Status.CONFIRMED),
        ),
    )

    stats_by_country = {
        item["tour__country_id"]: item
        for item in statistics
    }

    for country in countries:
        stats = stats_by_country.get(country.id, {})
        country.total_bookings = stats.get("total_bookings", 0)
        country.confirmed_bookings = stats.get("confirmed_bookings", 0)
        country.revenue = stats.get("revenue") or 0

    return render(
        request,
        "tours/country_statistics.html",
        {"countries": countries},
    )
