from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import BookingForm, FlightFilterForm, ReviewForm, SignupForm, StaffBookingForm
from .models import Booking, Flight, Review


class SignInView(LoginView):
    template_name = 'flights/login.html'


class SignOutView(LogoutView):
    pass


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        messages.success(request, 'Добро пожаловать на борт. Ваш аккаунт создан.')
        return redirect('flight_list')
    return render(request, 'flights/form.html', {'form': form, 'title': 'Начнём путешествие',
                  'eyebrow': 'ВАШ АККАУНТ', 'subtitle': 'Сохраняйте бронирования и делитесь впечатлениями.', 'button': 'Создать аккаунт'})


def flight_list(request):
    flights = Flight.objects.all()
    form = FlightFilterForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        for field in ['origin', 'destination']:
            if data[field]:
                flights = flights.filter(Q(**{f'{field}__icontains': data[field]}) | Q(**{f'{field}_code__iexact': data[field]}))
        if data['date']:
            flights = flights.filter(departure_at__date=data['date'])
        if data['q']:
            flights = flights.filter(Q(number__icontains=data['q']) | Q(airline__icontains=data['q']))
        for field in ['kind', 'status']:
            if data[field]:
                flights = flights.filter(**{field: data[field]})
    params = request.GET.copy()
    params.pop('page', None)
    tabs_params = params.copy()
    tabs_params.pop('kind', None)
    return render(request, 'flights/list.html', {'form': form, 'page': Paginator(flights, 6).get_page(request.GET.get('page')),
                  'query': params.urlencode(), 'tabs_query': tabs_params.urlencode(), 'total': flights.count(), 'today': timezone.localdate()})


def flight_detail(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    reviews = flight.reviews.select_related('user')
    review_form = ReviewForm(request.POST or None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.flight = flight
            review.flight_date = timezone.localtime(flight.departure_at).date()
            review.save()
            messages.success(request, 'Спасибо! Ваш отзыв опубликован.')
            return redirect('flight_detail', pk=pk)
    own_booking = flight.bookings.filter(user=request.user).first() if request.user.is_authenticated else None
    return render(request, 'flights/detail.html', {'flight': flight, 'review_form': review_form,
                  'reviews': reviews, 'rating': reviews.aggregate(value=Avg('rating'))['value'], 'own_booking': own_booking})


@login_required
def booking_edit(request, flight_pk=None, pk=None):
    booking = get_object_or_404(Booking, pk=pk, user=request.user) if pk else Booking(user=request.user)
    flight = booking.flight if pk else get_object_or_404(Flight, pk=flight_pk)
    if not pk and flight.bookings.filter(user=request.user).exists():
        messages.info(request, 'У вас уже есть бронирование на этот рейс.')
        return redirect('bookings')
    if flight.departure_at <= timezone.now() or flight.status == Flight.Status.DEPARTED:
        messages.error(request, 'Бронирование на этот рейс уже закрыто.')
        return redirect('flight_detail', pk=flight.pk)
    form = BookingForm(request.POST or None, instance=booking, flight=flight,
                       initial={'passenger_name': request.user.get_full_name()} if not pk else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                changed = form.save(commit=False)
                if pk:
                    changed.checked_in = False
                    changed.ticket_number = ''
                changed.save()
        except IntegrityError:
            form.add_error('seat', 'Это место только что забронировали. Выберите другое.')
        else:
            messages.success(request, 'Бронирование сохранено. До встречи на борту!')
            return redirect('bookings')
    return render(request, 'flights/form.html', {'form': form, 'flight': flight,
                  'title': 'Изменить бронирование' if pk else 'Ваше следующее путешествие',
                  'eyebrow': 'БРОНИРОВАНИЕ', 'subtitle': str(flight), 'button': 'Сохранить бронирование'})


@login_required
def bookings(request):
    return render(request, 'flights/bookings.html', {'bookings': request.user.bookings.select_related('flight')})


@login_required
@require_POST
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    booking.delete()
    messages.success(request, 'Бронирование отменено.')
    return redirect('bookings')


@login_required
def passengers(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    passengers = flight.bookings.order_by('passenger_name')
    q = request.GET.get('q', '').strip()
    if q:
        passengers = passengers.filter(passenger_name__icontains=q)
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'flights/passengers.html', {'flight': flight,
                  'page': Paginator(passengers, 10).get_page(request.GET.get('page')), 'query': params.urlencode(), 'q': q})


@user_passes_test(lambda user: user.is_active and user.is_staff)
def staff_booking(request, flight_pk, pk=None):
    flight = get_object_or_404(Flight, pk=flight_pk)
    booking = get_object_or_404(Booking, pk=pk, flight=flight) if pk else Booking(flight=flight)
    form = StaffBookingForm(request.POST or None, instance=booking, flight=flight)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error('seat', 'Место уже занято. Выберите другое.')
        else:
            messages.success(request, 'Данные пассажира сохранены.')
            return redirect('passengers', pk=flight.pk)
    return render(request, 'flights/form.html', {'form': form, 'title': 'Регистрация пассажира',
                  'eyebrow': 'УПРАВЛЕНИЕ РЕЙСОМ', 'subtitle': str(flight), 'button': 'Сохранить пассажира'})
