from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Tour, Booking
from .forms import BookingForm, RegisterForm, ReviewForm
from django.contrib import messages
from django.db.models import Count, Sum
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

def tour_list(request):
    tours = Tour.objects.all()

    query = request.GET.get('q', '').strip()
    availability = request.GET.get('availability', '')

    if query:
        tours = tours.filter(country__icontains=query)

    if availability == 'available':
        tours = [
            tour for tour in tours
            if tour.available_places > 0
        ]

    elif availability == 'full':
        tours = [
            tour for tour in tours
            if tour.available_places == 0
        ]

    paginator = Paginator(tours, 2)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'main_app/tour_list.html',
        {
            'tours': page_obj,
            'page_obj': page_obj,
            'query': query,
            'availability': availability,
        }
    )

def tour_detail(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    return render(
        request,
        'main_app/tour_detail.html',
        {'tour': tour}
    )


@login_required
def book_tour(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)

            booking.user = request.user
            booking.tour = tour

            if booking.people_count > tour.available_places:
                messages.error(
                    request,
                    f"Недостаточно мест. Свободно: {tour.available_places}"
                )
            else:
                booking.save()

                messages.success(
                    request,
                    "Тур успешно забронирован!"
                )

                return redirect('tour_detail', pk=pk)

    else:
        form = BookingForm()

    return render(
        request,
        'main_app/booking_form.html',
        {
            'form': form,
            'tour': tour
        }
    )


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)

    return render(
        request,
        "main_app/my_bookings.html",
        {"bookings": bookings}
    )

@login_required
def delete_booking(request, pk):
    booking = get_object_or_404(
        Booking,
        pk=pk,
        user=request.user
    )

    booking.delete()

    return redirect("my_bookings")

@login_required
def edit_booking(request, pk):
    booking = get_object_or_404(
        Booking,
        pk=pk,
        user=request.user
    )

    # Свободные места + места, которые уже занимает эта бронь
    available_for_edit = (
        booking.tour.available_places + booking.people_count
    )

    if request.method == "POST":
        form = BookingForm(
            request.POST,
            instance=booking
        )

        if form.is_valid():
            updated_booking = form.save(commit=False)

            if updated_booking.people_count > available_for_edit:
                messages.error(
                    request,
                    f"Недостаточно мест. Максимально доступно: {available_for_edit}"
                )
            else:
                updated_booking.save()

                messages.success(
                    request,
                    "Бронирование успешно изменено!"
                )

                return redirect("my_bookings")

    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        "main_app/edit_booking.html",
        {
            "form": form,
            "booking": booking,
            "available_for_edit": available_for_edit,
        }
    )

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Регистрация прошла успешно!"
            )

            return redirect("tour_list")
    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form}
    )


@login_required
def add_review(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)

            review.user = request.user
            review.tour = tour

            review.save()

            messages.success(
                request,
                "Отзыв успешно добавлен!"
            )

            return redirect("tour_detail", pk=pk)

    else:
        form = ReviewForm()

    return render(
        request,
        "main_app/review_form.html",
        {
            "form": form,
            "tour": tour
        }
    )

@user_passes_test(lambda user: user.is_staff)
def sales_by_country(request):
    sales = (
        Booking.objects
        .filter(status='confirmed')
        .values('tour__country')
        .annotate(
            bookings_count=Count('id'),
            people_count=Sum('people_count')
        )
        .order_by('tour__country')
    )

    return render(
        request,
        'main_app/sales_by_country.html',
        {'sales': sales}
    )