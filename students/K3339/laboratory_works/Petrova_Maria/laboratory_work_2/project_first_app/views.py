from django.shortcuts import get_object_or_404, redirect, render
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from .models import Reservation, Review, Room, Stay
from django.contrib.auth.decorators import login_required
from .forms import ReservationForm, ReviewForm


def register(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    else:

        form = UserCreationForm()

    return render(
        request,
        'project_first_app/register.html',
        {'form': form}

    )

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import Reservation, Review, Room, RoomType


def room_list(request):
    rooms = Room.objects.select_related(
    'hotel',
    'room_type'
    ).prefetch_related(
        'amenities'
    ).order_by('id')

    search = request.GET.get('search', '')
    room_type = request.GET.get('room_type', '')
    min_capacity = request.GET.get('min_capacity', '')
    max_price = request.GET.get('max_price', '')

    if search:
        rooms = rooms.filter(
            hotel__name__icontains=search
        )

    if room_type:
        rooms = rooms.filter(
            room_type_id=room_type
        )

    if min_capacity:
        rooms = rooms.filter(
            capacity__gte=min_capacity
        )

    if max_price:
        rooms = rooms.filter(
            price__lte=max_price
        )

    paginator = Paginator(rooms, 6)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    room_types = RoomType.objects.all()

    return render(
        request,
        'project_first_app/room_list.html',
        {
            'page_obj': page_obj,
            'room_types': room_types,
            'search': search,
            'selected_room_type': room_type,
            'min_capacity': min_capacity,
            'max_price': max_price,
        }
    )


def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    return render(
        request,
        'project_first_app/room_detail.html',
        {'room': room}
    )

@login_required
def create_reservation(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=Reservation(room=room))

        if form.is_valid():
            reservation = form.save(commit=False)

            reservation.user = request.user
            reservation.room = room

            reservation.save()

            return redirect('my_reservations')

    else:
        form = ReservationForm(instance=Reservation(room=room))

    return render(
        request,
        'project_first_app/reservation_form.html',
        {
            'form': form,
            'room': room
        }
    )
@login_required
def my_reservations(request):
    reservations = request.user.reservations.all()

    return render(
        request,
        'project_first_app/my_reservations.html',
        {'reservations': reservations}
    )

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user
    )

    if request.method == 'POST':
        form = ReservationForm(
            request.POST,
            instance=reservation
        )

        if form.is_valid():
            form.save()
            return redirect('my_reservations')

    else:
        form = ReservationForm(instance=reservation)

    return render(
        request,
        'project_first_app/reservation_form.html',
        {
            'form': form,
            'room': reservation.room,
            'is_edit': True,
        }
    )


@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user
    )

    if request.method == 'POST':
        reservation.delete()
        return redirect('my_reservations')

    return render(
        request,
        'project_first_app/reservation_confirm_delete.html',
        {'reservation': reservation}
    )

@login_required
def create_review(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)

            review.user = request.user
            review.room = room

            review.save()

            return redirect('room_detail', room_id=room.id)

    else:
        form = ReviewForm()

    return render(
        request,
        'project_first_app/review_form.html',
        {
            'form': form,
            'room': room,
        }
    )

@login_required
def recent_guests(request):
    if not request.user.is_staff:
        return redirect('room_list')

    current_datetime = timezone.now()
    month_ago = current_datetime - timedelta(days=30)

    stays = Stay.objects.filter(
        Q(check_out__isnull=True) | Q(check_out__gte=month_ago),
        check_in__lte=current_datetime,
    ).select_related(
        'user',
        'room',
        'room__hotel'
    ).order_by('-check_in')

    return render(
        request,
        'project_first_app/recent_guests.html',
        {'stays': stays}
    )
