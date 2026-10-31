from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Min, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import RegisterForm, ReservationForm, ReviewForm
from .models import Amenity, Hotel, Reservation, Review, Room

staff_required = user_passes_test(lambda u: u.is_staff)


def paginate(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно')
            return redirect('hotel_list')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def hotel_list(request):
    hotels = Hotel.objects.annotate(
        min_price=Min('rooms__price'),
        rooms_count=Count('rooms', distinct=True),
    )

    q = request.GET.get('q', '').strip()
    city = request.GET.get('city', '')
    amenity = request.GET.get('amenity', '')

    if q:
        hotels = hotels.filter(Q(name__icontains=q) | Q(address__icontains=q) | Q(description__icontains=q))
    if city:
        hotels = hotels.filter(city=city)
    if amenity:
        hotels = hotels.filter(amenities__id=amenity)

    context = {
        'page_obj': paginate(request, hotels.order_by('name'), 6),
        'cities': Hotel.objects.values_list('city', flat=True).distinct().order_by('city'),
        'amenities': Amenity.objects.all(),
        'q': q,
        'city': city,
        'amenity': amenity,
    }
    return render(request, 'hotels/hotel_list.html', context)


def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    rooms = hotel.rooms.annotate(avg_rating=Avg('reviews__rating')).prefetch_related('amenities').order_by('number')

    room_type = request.GET.get('type', '')
    guests = request.GET.get('guests', '')
    max_price = request.GET.get('max_price', '')

    if room_type:
        rooms = rooms.filter(room_type=room_type)
    if guests.isdigit():
        rooms = rooms.filter(capacity__gte=int(guests))
    if max_price.isdigit():
        rooms = rooms.filter(price__lte=int(max_price))

    context = {
        'hotel': hotel,
        'page_obj': paginate(request, rooms, 5),
        'types': Room.TYPES,
        'room_type': room_type,
        'guests': guests,
        'max_price': max_price,
    }
    return render(request, 'hotels/hotel_detail.html', context)


def room_detail(request, pk):
    room = get_object_or_404(Room.objects.select_related('hotel'), pk=pk)
    reviews = room.reviews.select_related('user')
    context = {
        'room': room,
        'page_obj': paginate(request, reviews, 5),
        'avg_rating': reviews.aggregate(avg=Avg('rating'))['avg'],
        'today': timezone.localdate(),
    }
    if request.user.is_staff:
        context['reservations'] = room.reservations.select_related('user').exclude(status='cancelled')
    else:
        context['busy'] = room.reservations.filter(
            status__in=['booked', 'checked_in'],
            date_to__gte=timezone.localdate(),
        ).order_by('date_from')
    return render(request, 'hotels/room_detail.html', context)


@login_required
def reservation_create(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST, room=room)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.room = room
            reservation.save()
            messages.success(request, 'Номер забронирован')
            return redirect('my_reservations')
    else:
        form = ReservationForm(room=room)
    return render(request, 'hotels/reservation_form.html', {'form': form, 'room': room})


@login_required
def reservation_edit(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if not reservation.can_edit():
        messages.error(request, 'Это бронирование уже нельзя изменить')
        return redirect('my_reservations')
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Бронирование изменено')
            return redirect('my_reservations')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'hotels/reservation_form.html', {'form': form, 'room': reservation.room, 'edit': True})


@login_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if not reservation.can_edit():
        messages.error(request, 'Это бронирование уже нельзя удалить')
        return redirect('my_reservations')
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, 'Бронирование удалено')
        return redirect('my_reservations')
    return render(request, 'hotels/reservation_delete.html', {'reservation': reservation})


@login_required
def my_reservations(request):
    reservations = request.user.reservations.select_related('room__hotel')
    status = request.GET.get('status', '')
    if status:
        reservations = reservations.filter(status=status)
    context = {
        'page_obj': paginate(request, reservations, 8),
        'statuses': Reservation.STATUSES,
        'status': status,
    }
    return render(request, 'hotels/my_reservations.html', context)


@login_required
def review_create(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.room = room
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('room_detail', pk=room.pk)
    else:
        last_stay = request.user.reservations.filter(room=room, status='checked_out').first()
        initial = {}
        if last_stay:
            initial = {'date_from': last_stay.date_from, 'date_to': last_stay.date_to}
        form = ReviewForm(initial=initial)
    return render(request, 'hotels/review_form.html', {'form': form, 'room': room})


@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    room_id = review.room_id
    review.delete()
    messages.success(request, 'Отзыв удален')
    return redirect('room_detail', pk=room_id)


def guests(request):
    today = timezone.localdate()
    month_ago = today - timedelta(days=30)
    stays = Reservation.objects.filter(
        status__in=['checked_in', 'checked_out'],
        date_from__lte=today,
        date_to__gte=month_ago,
    ).select_related('user', 'room__hotel').order_by('room__hotel__name', 'date_from')

    hotel = request.GET.get('hotel', '')
    q = request.GET.get('q', '').strip()
    if hotel:
        stays = stays.filter(room__hotel_id=hotel)
    if q:
        stays = stays.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(user__username__icontains=q)
        )

    context = {
        'page_obj': paginate(request, stays, 10),
        'hotels': Hotel.objects.all(),
        'hotel': hotel,
        'q': q,
        'month_ago': month_ago,
        'today': today,
    }
    return render(request, 'hotels/guests.html', context)


@staff_required
def manage_reservations(request):
    reservations = Reservation.objects.select_related('user', 'room__hotel').order_by('date_from')

    status = request.GET.get('status', 'booked')
    hotel = request.GET.get('hotel', '')
    q = request.GET.get('q', '').strip()
    if status:
        reservations = reservations.filter(status=status)
    if hotel:
        reservations = reservations.filter(room__hotel_id=hotel)
    if q:
        reservations = reservations.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(user__username__icontains=q)
        )

    context = {
        'page_obj': paginate(request, reservations, 10),
        'statuses': Reservation.STATUSES,
        'hotels': Hotel.objects.all(),
        'status': status,
        'hotel': hotel,
        'q': q,
    }
    return render(request, 'hotels/manage_reservations.html', context)


@staff_required
@require_POST
def change_status(request, pk, action):
    reservation = get_object_or_404(Reservation, pk=pk)
    if action == 'check_in' and reservation.status == 'booked':
        reservation.status = 'checked_in'
        reservation.checked_in_at = timezone.now()
        reservation.save()
        messages.success(request, f'{reservation.user.get_full_name()} заселен(а)')
    elif action == 'check_out' and reservation.status == 'checked_in':
        reservation.status = 'checked_out'
        reservation.checked_out_at = timezone.now()
        reservation.save()
        messages.success(request, f'{reservation.user.get_full_name()} выселен(а)')
    elif action == 'cancel' and reservation.status == 'booked':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Бронирование отменено')
    else:
        messages.error(request, 'Это действие недоступно для текущего статуса')

    next_url = request.POST.get('next', '')
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('manage_reservations')
