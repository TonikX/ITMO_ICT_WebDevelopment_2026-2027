import calendar
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.functions import Collate, Upper
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingForm, ReviewForm, RoomFilterForm
from .models import Booking, Hotel, Review, Room


def page_context(request, queryset):
    params = request.GET.copy()
    params.pop("page", None)
    return {
        "page": Paginator(queryset, 6).get_page(request.GET.get("page")),
        "query": params.urlencode(),
    }


def room_list(request):
    rooms = Room.objects.select_related("hotel")
    form = RoomFilterForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        if data["q"]:
            # ICU обрабатывает кириллицу даже при локали базы C.
            query = data["q"].upper()
            rooms = rooms.alias(
                search_name=Upper(Collate("hotel__name", "und-x-icu")),
                search_address=Upper(Collate("hotel__address", "und-x-icu")),
                search_amenities=Upper(Collate("amenities", "und-x-icu")),
            ).filter(
                Q(search_name__contains=query)
                | Q(search_address__contains=query)
                | Q(search_amenities__contains=query)
            )
        if data["room_type"]:
            rooms = rooms.filter(room_type=data["room_type"])
        if data["capacity"]:
            rooms = rooms.filter(capacity__gte=data["capacity"])
        if data["max_price"]:
            rooms = rooms.filter(price__lte=data["max_price"])
    else:
        rooms = rooms.none()
    return render(
        request, "room_list.html", {"form": form, **page_context(request, rooms)}
    )


def room_detail(request, pk):
    room = get_object_or_404(Room.objects.select_related("hotel"), pk=pk)
    reviews = room.reviews.select_related("user")
    return render(request, "room_detail.html", {"room": room, "reviews": reviews})


def signup(request):
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        messages.success(
            request, "Вы зарегистрированы. Теперь можно бронировать номера."
        )
        return redirect("room_list")
    return render(
        request,
        "form.html",
        {"form": form, "title": "Регистрация", "button": "Зарегистрироваться"},
    )


@login_required
def booking_create(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    booking = Booking(room=room, user=request.user)
    form = BookingForm(
        request.POST if request.method == "POST" else None, instance=booking
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Номер забронирован.")
        return redirect("my_bookings")
    return render(
        request,
        "form.html",
        {"form": form, "title": f"Бронирование: {room}", "button": "Забронировать"},
    )


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("room__hotel")
    return render(request, "bookings.html", {"bookings": bookings})


@login_required
def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    form = BookingForm(
        request.POST if request.method == "POST" else None, instance=booking
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Бронирование изменено.")
        return redirect("my_bookings")
    return render(
        request,
        "form.html",
        {"form": form, "title": "Изменить бронирование", "button": "Сохранить"},
    )


@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Бронирование удалено.")
        return redirect("my_bookings")
    return render(request, "confirm_delete.html", {"booking": booking})


@login_required
def review_create(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    review = Review(room=room, user=request.user)
    form = ReviewForm(
        request.POST if request.method == "POST" else None, instance=review
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Отзыв добавлен.")
        return redirect("room_detail", pk=room.pk)
    return render(
        request,
        "form.html",
        {"form": form, "title": f"Отзыв: {room}", "button": "Опубликовать отзыв"},
    )


def is_staff(user):
    return user.is_active and (user.is_staff or user.is_superuser)


@user_passes_test(is_staff)
def guest_report(request):
    today = timezone.localdate()
    prev_month = today.replace(day=1) - timedelta(days=1)
    start = today.replace(
        year=prev_month.year,
        month=prev_month.month,
        day=min(today.day, calendar.monthrange(prev_month.year, prev_month.month)[1]),
    )
    # В отчёт попадают реальные постояльцы, чьё проживание пересекает последний месяц.
    bookings = (
        Booking.objects.filter(checked_in_at__lte=today)
        .filter(Q(checked_out_at__gte=start) | Q(checked_out_at__isnull=True))
        .select_related("user", "room__hotel")
    )
    try:
        hotel_id = int(request.GET.get("hotel", ""))
    except ValueError:
        hotel_id = None
    if hotel_id is not None:
        bookings = bookings.filter(room__hotel_id=hotel_id)
    return render(
        request,
        "guest_report.html",
        {
            "hotels": Hotel.objects.all(),
            "hotel_id": hotel_id,
            "start": start,
            "today": today,
            **page_context(request, bookings),
        },
    )
