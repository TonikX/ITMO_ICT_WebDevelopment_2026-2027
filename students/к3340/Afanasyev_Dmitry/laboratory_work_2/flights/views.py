from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import BookingForm, CheckInForm, FlightFilterForm, FlightForm, ReviewForm
from .models import Booking, Flight, Review
from .pagination import paginate, InvalidCursor


def require_staff(user):
    if not (user.is_staff or user.is_superuser):
        raise PermissionDenied


def flight_list(request):
    qs = Flight.objects.select_related('airline').annotate(booked=Count('bookings'))
    form = FlightFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['origin']:
            qs = qs.filter(origin__icontains=form.cleaned_data['origin'])
        if form.cleaned_data['destination']:
            qs = qs.filter(destination__icontains=form.cleaned_data['destination'])
        q = form.cleaned_data['q']
        if q:
            qs = qs.filter(Q(number__icontains=q) | Q(origin__icontains=q) |
                           Q(destination__icontains=q) | Q(airline__name__icontains=q))
        if form.cleaned_data['direction']:
            qs = qs.filter(direction=form.cleaned_data['direction'])
        if form.cleaned_data['date']:
            qs = qs.filter(departure_at__date=form.cleaned_data['date'])
        if form.cleaned_data['available']:
            qs = qs.filter(booked__lt=F('capacity'), departure_at__gt=timezone.now(),
                           status__in=['scheduled', 'boarding', 'delayed'])
    else:
        qs = qs.none()
    try:
        page = paginate(qs, request.GET.get('cursor'), form.cleaned_data if form.is_valid() else {})
    except InvalidCursor as error:
        messages.error(request, str(error))
        page = paginate(qs, None, form.cleaned_data if form.is_valid() else {})
    params = request.GET.copy()
    params.pop('cursor', None)
    return render(request, 'flight_list.html', {'page': page, 'form': form, 'query': params.urlencode()})


def flight_detail(request, pk):
    flight = get_object_or_404(Flight.objects.select_related('airline'), pk=pk)
    booking = flight.bookings.filter(user=request.user).first() if request.user.is_authenticated else None
    reviews = flight.reviews.select_related('user')
    return render(request, 'flight_detail.html', {'flight': flight, 'booking': booking,
        'free': flight.capacity - flight.bookings.count(), 
        'reviewed': request.user.is_authenticated and reviews.filter(user=request.user).exists()})


@login_required
def booking_create(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if not flight.is_bookable:
        messages.error(request, 'Бронирование этого рейса закрыто.')
        return redirect(flight)
    if flight.bookings.filter(user=request.user).exists():
        messages.info(request, 'У вас уже есть бронирование на этот рейс.')
        return redirect('booking_list')
    form = BookingForm(request.POST or None, flight=flight,
                       initial={'passenger_name': request.user.get_full_name() or request.user.username})
    form.instance.user = request.user
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except (ValidationError, IntegrityError):
            form.add_error(None, 'Место уже занято или рейс недоступен. Обновите страницу и выберите другое место.')
        else:
            messages.success(request, 'Место забронировано.')
            return redirect('booking_list')
    return render(request, 'form.html', {'form': form, 'title': f'Бронирование · {flight.number}',
        'subtitle': str(flight), 'submit': 'Забронировать', 'back_url': flight.get_absolute_url()})


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).select_related('flight', 'flight__airline')
    return render(request, 'booking_list.html', {'bookings': bookings})


@login_required
def booking_edit(request, pk):
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update().select_related('flight'), pk=pk, user=request.user)
        if booking.checked_in or not booking.flight.is_bookable:
            messages.error(request, 'После регистрации или закрытия рейса бронирование изменить нельзя.')
            return redirect('booking_list')
        form = BookingForm(request.POST or None, instance=booking, flight=booking.flight)
        if request.method == 'POST' and form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
            except (ValidationError, IntegrityError):
                form.add_error(None, 'Место уже занято. Выберите другое место.')
            else:
                messages.success(request, 'Бронирование обновлено.')
                return redirect('booking_list')
    return render(request, 'form.html', {'form': form, 'title': 'Редактирование бронирования',
        'submit': 'Сохранить', 'back_url': '/bookings/'})


@login_required
def booking_delete(request, pk):
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update().select_related('flight'), pk=pk, user=request.user)
        if booking.checked_in or not booking.flight.is_bookable:
            messages.error(request, 'После регистрации или закрытия рейса отмена недоступна.')
            return redirect('booking_list')
        if request.method == 'POST':
            booking.delete()
            messages.success(request, 'Бронирование отменено, место снова свободно.')
            return redirect('booking_list')
    return render(request, 'confirm_delete.html', {'object': booking, 'back_url': '/bookings/'})


@login_required
def review_create(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    if not flight.bookings.filter(user=request.user).exists():
        raise PermissionDenied('Отзыв может оставить только пассажир рейса.')
    if flight.reviews.filter(user=request.user).exists():
        messages.info(request, 'Вы уже оставили отзыв.')
        return redirect(flight)
    form = ReviewForm(request.POST or None)
    form.instance.flight = flight
    form.instance.user = request.user
    form.instance.flight_date = timezone.localtime(flight.departure_at).date()
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except (ValidationError, IntegrityError):
            form.add_error(None, 'Отзыв уже существует или данные некорректны.')
        else:
            messages.success(request, 'Отзыв опубликован.')
            return redirect(flight)
    return render(request, 'form.html', {'form': form, 'title': f'Отзыв о рейсе {flight.number}',
        'submit': 'Опубликовать отзыв', 'back_url': flight.get_absolute_url()})


@login_required
def passenger_list(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    require_staff(request.user)
    passengers = flight.bookings.select_related('user').order_by('seat')
    return render(request, 'passengers.html', {'flight': flight, 'passengers': passengers})


@login_required
def check_in(request, pk):
    require_staff(request.user)
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update().select_related('flight'), pk=pk)
        if booking.flight.status in ['cancelled', 'completed'] or booking.flight.departure_at <= timezone.now():
            messages.error(request, 'Регистрация на этот рейс закрыта.')
            return redirect('passengers', pk=booking.flight_id)
        form = CheckInForm(request.POST or None, instance=booking)
        if request.method == 'POST' and form.is_valid():
            booking.checked_in = True
            try:
                with transaction.atomic():
                    booking.save()
            except (ValidationError, IntegrityError):
                form.add_error('ticket_number', 'Номер билета уже используется или некорректен.')
            else:
                messages.success(request, 'Пассажир зарегистрирован на рейс.')
                return redirect('passengers', pk=booking.flight_id)
    return render(request, 'form.html', {'form': form, 'title': 'Регистрация пассажира',
        'subtitle': str(booking), 'submit': 'Зарегистрировать',
        'back_url': booking.flight.get_absolute_url()})


@login_required
def flight_edit(request, pk=None):
    require_staff(request.user)
    flight = get_object_or_404(Flight, pk=pk) if pk else None
    form = FlightForm(request.POST or None, instance=flight)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                result = form.save()
        except (ValidationError, IntegrityError):
            form.add_error(None, 'Сохранение невозможно: проверьте даты, места и уникальность рейса.')
        else:
            messages.success(request, 'Рейс сохранён.')
            return redirect(result)
    return render(request, 'form.html', {'form': form, 'title': 'Изменить рейс' if pk else 'Новый рейс',
        'submit': 'Сохранить рейс', 'back_url': '/'})
