from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import BookingForm, CommentForm, SignUpForm, TicketForm
from .models import Booking, Comment, Flight


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


def board(request):
    flights = Flight.objects.all()
    query = request.GET.get('q', '')
    kind = request.GET.get('kind', '')
    if query:
        flights = flights.filter(
            Q(number__icontains=query) | Q(airline__icontains=query)
            | Q(from_city__icontains=query) | Q(to_city__icontains=query)
        )
    if kind:
        flights = flights.filter(kind=kind)
    page = Paginator(flights, 5).get_page(request.GET.get('page'))
    return render(request, 'board.html', {'page': page, 'query': query, 'kind': kind})


def flight_page(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    passengers = flight.bookings.select_related('passenger').order_by('seat')
    comments = flight.comments.select_related('author').order_by('-id')
    context = {
        'flight': flight,
        'passengers': passengers,
        'comments': comments,
        'free': flight.seats - passengers.count(),
    }
    return render(request, 'flight.html', context)


@login_required
def book_seat(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    booking = Booking(flight=flight, passenger=request.user)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('my_bookings')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_form.html', {'form': form, 'flight': flight})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(passenger=request.user).select_related('flight').order_by('flight__takeoff', 'seat')
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def change_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, passenger=request.user, checked_in=False)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('my_bookings')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_form.html', {'form': form, 'flight': booking.flight})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, passenger=request.user, checked_in=False)
    if request.method == 'POST':
        booking.delete()
        return redirect('my_bookings')
    return render(request, 'booking_cancel.html', {'booking': booking})


@login_required
def add_comment(request, pk):
    flight = get_object_or_404(Flight, pk=pk)
    comment = Comment(flight=flight, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('flight', pk=pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'comment_form.html', {'form': form, 'flight': flight})


@staff_member_required
def check_in(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('flight', pk=booking.flight.pk)
    else:
        form = TicketForm(instance=booking)
    return render(request, 'check_in.html', {'form': form, 'booking': booking})
