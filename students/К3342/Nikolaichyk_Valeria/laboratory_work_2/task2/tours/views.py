from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.contrib import messages
from .forms import BookingForm, ReviewForm
from .models import Tour, Booking, Review
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum

def home(request):
    tours = Tour.objects.all().order_by('start_date')

    # Поиск по названию тура
    search_query = request.GET.get('q', '')
    if search_query:
        tours = tours.filter(title__icontains=search_query)

    # Фильтрация по стране
    country = request.GET.get('country', '')
    if country:
        tours = tours.filter(country__iexact=country)

    paginator = Paginator(tours, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    countries = Tour.objects.values_list('country', flat=True).distinct().order_by('country')
    return render(request, 'tours/home.html', {
        'tours': page_obj,
        'page_obj': page_obj,
        'countries': countries,
        'search_query': search_query,
        'selected_country': country,
    })

def tour_detail(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    reviews = Review.objects.filter(
        tour=tour
    ).select_related('user').order_by('-created_at')

    return render(request, 'tours/tour_detail.html', {
        'tour': tour,
        'reviews': reviews,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
@require_POST
def book_tour(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    booked_places = sum(
        booking.places
        for booking in Booking.objects.filter(tour=tour,status__in=[ Booking.Status.PENDING,Booking.Status.CONFIRMED,]))

    remaining_places = tour.available_places - booked_places

    if remaining_places < 1:
        messages.error(request, 'К сожалению, свободных мест больше нет.')
    else:
        Booking.objects.create(user=request.user,tour=tour,places=1 )
        messages.success( request,'Заявка на бронирование отправлена и ожидает подтверждения.')

    return redirect('tour_detail', tour_id=tour.id)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('tour').order_by('-booking_date')

    return render(request, 'tours/my_bookings.html', {'bookings': bookings})

@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking,id=booking_id,user=request.user)

    if booking.status != Booking.Status.PENDING:
        messages.error(request,'Можно редактировать только заявки, ожидающие подтверждения.')
        return redirect('my_bookings')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)

        if form.is_valid():
            new_places = form.cleaned_data['places']

            other_bookings = Booking.objects.filter(
                tour=booking.tour,
                status__in=[Booking.Status.PENDING,Booking.Status.CONFIRMED,]).exclude(id=booking.id)

            already_booked = sum(item.places for item in other_bookings)

            if already_booked + new_places > booking.tour.available_places:
                form.add_error('places','Недостаточно свободных мест.')
            else:
                form.save()
                messages.success(request, 'Бронирование обновлено.')
                return redirect('my_bookings')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'tours/edit_booking.html', {'form': form,'booking': booking,})

@login_required
@require_POST
def delete_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.status == Booking.Status.PENDING:
        booking.delete()
        messages.success(request, 'Бронирование успешно удалено.')
    else:
        messages.error(
            request,
            'Можно удалить только заявки, ожидающие подтверждения.'
        )

    return redirect('my_bookings')
@login_required
def add_review(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.tour = tour
            review.save()

            messages.success(request, 'Ваш отзыв успешно опубликован.')
            return redirect('tour_detail', tour_id=tour.id)
    else:
        form = ReviewForm()

    return render(request, 'tours/add_review.html', {
        'form': form,
        'tour': tour,
    })

@user_passes_test(lambda user: user.is_staff)
def manage_bookings(request):
    bookings = Booking.objects.select_related(
        'user', 'tour'
    ).order_by('-booking_date')

    return render(request, 'tours/manage_bookings.html', {
        'bookings': bookings,
    })

@login_required
@user_passes_test(lambda user: user.is_staff)
@require_POST
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.CONFIRMED
        booking.save()
        messages.success(request, 'Бронирование подтверждено.')
    else:
        messages.error(request, 'Эта заявка уже обработана.')

    return redirect('manage_bookings')


def sales_statistics(request):
    statistics = Booking.objects.filter(
        status=Booking.Status.CONFIRMED
    ).values(
        'tour__country'
    ).annotate(
        sold_places=Sum('places')
    ).order_by('tour__country')

    return render(request, 'tours/sales_statistics.html', {
        'statistics': statistics,
    })