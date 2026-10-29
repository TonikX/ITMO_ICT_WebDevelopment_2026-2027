from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from functools import wraps
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import BookingForm, RegistrationForm, ReviewForm, SearchForm
from .models import Booking, Hotel, Review, Room


def page_context(request, objects, per_page=6):
    query = request.GET.copy()
    query.pop('page', None)
    return {'page': Paginator(objects, per_page).get_page(request.GET.get('page')), 'query': query.urlencode()}


def room_list(request):
    rooms = Room.objects.select_related('hotel')
    form = SearchForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        if data['q']:
            rooms = rooms.filter(Q(hotel__name__icontains=data['q']) | Q(hotel__city__icontains=data['q']))
        if data['room_type']:
            rooms = rooms.filter(room_type=data['room_type'])
        if data['capacity']:
            rooms = rooms.filter(capacity__gte=data['capacity'])
        if data['max_price']:
            rooms = rooms.filter(price__lte=data['max_price'])
        if data['arrival'] and data['departure']:
            busy = Booking.objects.filter(status__in=[Booking.BOOKED, Booking.IN],
                arrival__lt=data['departure'], departure__gt=data['arrival']).values('room_id')
            rooms = rooms.exclude(pk__in=busy)
    else:
        rooms = rooms.none()
    return render(request, 'rooms.html', {'form': form, **page_context(request, rooms)})


def room_detail(request, pk):
    room = get_object_or_404(Room.objects.select_related('hotel'), pk=pk)
    reviews = room.reviews.select_related('user')
    return render(request, 'room.html', {'room': room, **page_context(request, reviews, 5)})


def register(request):
    if request.user.is_authenticated:
        return redirect('room_list')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Аккаунт создан.')
        return redirect('room_list')
    return render(request, 'form.html', {'form': form, 'title': 'Регистрация', 'button': 'Создать аккаунт'})


@require_POST
def sign_out(request):
    logout(request)
    return redirect('room_list')


@login_required
def booking_create(request, pk):
    room = get_object_or_404(Room.objects.select_related('hotel'), pk=pk)
    booking = Booking(room=room, user=request.user)
    return booking_form(request, booking, f'Бронирование: {room}')


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('room__hotel'), pk=pk, user=request.user, status=Booking.BOOKED)
    return booking_form(request, booking, 'Изменить бронирование')


def booking_form(request, booking, title):
    with transaction.atomic():
        Room.objects.select_for_update().get(pk=booking.room_id)
        # Общая блокировка номера сериализует проверку и сохранение бронирований.
        if booking.pk:
            booking = Booking.objects.select_for_update().get(pk=booking.pk)
            if booking.status != Booking.BOOKED:
                messages.error(request, 'Бронирование уже изменено администратором.')
                return redirect('my_bookings')
        form = BookingForm(request.POST if request.method == 'POST' else None, instance=booking)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, 'Бронирование сохранено.')
            return redirect('my_bookings')
    return render(request, 'form.html', {'form': form, 'title': title, 'button': 'Сохранить', 'room': booking.room})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room__hotel', 'review')
    return render(request, 'bookings.html', page_context(request, bookings))


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('room__hotel'), pk=pk, user=request.user, status=Booking.BOOKED)
    if request.method == 'POST':
        with transaction.atomic():
            Room.objects.select_for_update().get(pk=booking.room_id)
            booking = get_object_or_404(Booking.objects.select_for_update(), pk=pk, user=request.user, status=Booking.BOOKED)
            booking.delete()
        messages.success(request, 'Бронирование удалено.')
        return redirect('my_bookings')
    return render(request, 'delete.html', {'booking': booking})


@login_required
def review_create(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('room__hotel'), pk=pk, user=request.user, status=Booking.OUT)
    with transaction.atomic():
        Booking.objects.select_for_update().get(pk=booking.pk)
        if Review.objects.filter(booking=booking).exists():
            messages.info(request, 'Отзыв об этом проживании уже опубликован.')
            return redirect('room_detail', pk=booking.room_id)
        review = Review(booking=booking, room=booking.room, user=request.user,
            arrival=timezone.localtime(booking.checked_in_at).date(), departure=timezone.localtime(booking.checked_out_at).date())
        form = ReviewForm(request.POST if request.method == 'POST' else None, instance=review)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, 'Отзыв опубликован.')
            return redirect('room_detail', pk=booking.room_id)
    return render(request, 'form.html', {'form': form, 'title': f'Отзыв: {booking.room}', 'button': 'Опубликовать'})


def staff_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped


@staff_required
def staff_bookings(request):
    bookings = Booking.objects.select_related('room__hotel', 'user')
    status = request.GET.get('status', '')
    hotel = request.GET.get('hotel', '')
    if status in dict(Booking.STATUS):
        bookings = bookings.filter(status=status)
    if hotel.isdigit():
        bookings = bookings.filter(room__hotel_id=hotel)
    return render(request, 'staff.html', {'hotels': Hotel.objects.all(), 'status': status,
        'hotel': hotel, 'statuses': Booking.STATUS, **page_context(request, bookings, 10)})


@staff_required
@require_POST
def staff_action(request, pk, action):
    with transaction.atomic():
        initial = get_object_or_404(Booking, pk=pk)
        Room.objects.select_for_update().get(pk=initial.room_id)
        booking = Booking.objects.select_for_update().get(pk=pk)
        try:
            booking.change_status(action)
            messages.success(request, 'Статус проживания обновлён.')
        except ValidationError as error:
            messages.error(request, ' '.join(error.messages))
    return redirect('staff_bookings')


@staff_required
def guests(request):
    end = timezone.now()
    start = end - timedelta(days=30)
    bookings = Booking.objects.select_related('room__hotel', 'user').filter(
        checked_in_at__lte=end).filter(Q(checked_out_at__gte=start) | Q(status=Booking.IN))
    hotel = request.GET.get('hotel', '')
    if hotel.isdigit():
        bookings = bookings.filter(room__hotel_id=hotel)
    return render(request, 'guests.html', {'hotels': Hotel.objects.all(), 'hotel': hotel,
        'start': timezone.localtime(start).date(), 'end': timezone.localtime(end).date(),
        **page_context(request, bookings, 10)})
