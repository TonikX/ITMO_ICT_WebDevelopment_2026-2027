from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Hotel, Room, Booking, Review
from .forms import CustomUserCreationForm
from django.contrib.admin.views.decorators import staff_member_required

class HotelListView(ListView):
    model = Hotel
    template_name = 'hotels_app/hotel_list.html'
    context_object_name = 'hotels'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        city = self.request.GET.get('city')
        if search:
            queryset = queryset.filter(name__icontains=search)
        if city:
            queryset = queryset.filter(address__icontains=city)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['city_query'] = self.request.GET.get('city', '')
        context['cities'] = Hotel.objects.values_list('address', flat=True).distinct()
        return context

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'hotels_app/register.html'
    success_url = reverse_lazy('login')

def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        if 'book' in request.POST:
            room = get_object_or_404(Room, pk=request.POST.get('room'))
            check_in = request.POST.get('check_in')
            check_out = request.POST.get('check_out')
            Booking.objects.create(user=request.user, room=room, check_in=check_in, check_out=check_out)
            return redirect('hotel_detail', pk=pk)
        elif 'review' in request.POST:
            room = get_object_or_404(Room, pk=request.POST.get('room'))
            Review.objects.create(
                user=request.user,
                room=room,
                text=request.POST.get('text'),
                rating=request.POST.get('rating'),
                stay_period=request.POST.get('stay_period')
            )
            return redirect('hotel_detail', pk=pk)
    return render(request, 'hotels_app/hotel_detail.html', {'hotel': hotel})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-check_in')
    return render(request, 'hotels_app/my_bookings.html', {'bookings': bookings})

@login_required
def booking_update(request, pk):
    if request.user.is_staff:
        booking = get_object_or_404(Booking, pk=pk)
    else:
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == 'POST':
        booking.check_in = request.POST.get('check_in')
        booking.check_out = request.POST.get('check_out')
        booking.save()
        return redirect('all_bookings' if request.user.is_staff else 'my_bookings')
    return render(request, 'hotels_app/booking_update.html', {'booking': booking})

@login_required
def booking_delete(request, pk):
    if request.user.is_staff:
        booking = get_object_or_404(Booking, pk=pk)
    else:
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if request.method == 'POST':
        booking.delete()
        return redirect('all_bookings' if request.user.is_staff else 'my_bookings')
    return render(request, 'hotels_app/booking_delete.html', {'booking': booking})

def guests_table(request):
    one_month_ago = timezone.now().date() - timedelta(days=30)
    bookings = Booking.objects.filter(check_in__gte=one_month_ago).order_by('-check_in')
    return render(request, 'hotels_app/guests_table.html', {'bookings': bookings})

@staff_member_required
def hotel_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        owner_name = request.POST.get('owner_name')
        address = request.POST.get('address')
        description = request.POST.get('description')
        stars = request.POST.get('stars')
        if name and owner_name and address and stars:
            Hotel.objects.create(name=name, owner_name=owner_name, address=address, description=description, stars=stars)
            return redirect('hotel_list')
    return render(request, 'hotels_app/hotel_form.html', {'action': 'Создать отель'})

@staff_member_required
def hotel_update(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        hotel.name = request.POST.get('name')
        hotel.owner_name = request.POST.get('owner_name')
        hotel.address = request.POST.get('address')
        hotel.description = request.POST.get('description')
        hotel.stars = request.POST.get('stars')
        hotel.save()
        return redirect('hotel_detail', pk=hotel.pk)
    return render(request, 'hotels_app/hotel_form.html', {'action': 'Редактировать отель', 'hotel': hotel})

@staff_member_required
def hotel_delete(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        hotel.delete()
        return redirect('hotel_list')
    return render(request, 'hotels_app/hotel_delete.html', {'hotel': hotel})

@staff_member_required
def room_create(request, hotel_pk):
    hotel = get_object_or_404(Hotel, pk=hotel_pk)
    if request.method == 'POST':
        room_type = request.POST.get('room_type')
        price = request.POST.get('price')
        capacity = request.POST.get('capacity')
        if room_type and price and capacity:
            Room.objects.create(hotel=hotel, room_type=room_type, price=price, capacity=capacity)
            return redirect('hotel_detail', pk=hotel.pk)
    return render(request, 'hotels_app/room_form.html', {'action': 'Добавить номер', 'hotel': hotel})

@staff_member_required
def all_bookings(request):
    bookings = Booking.objects.all().order_by('-check_in')
    return render(request, 'hotels_app/all_bookings.html', {'bookings': bookings})