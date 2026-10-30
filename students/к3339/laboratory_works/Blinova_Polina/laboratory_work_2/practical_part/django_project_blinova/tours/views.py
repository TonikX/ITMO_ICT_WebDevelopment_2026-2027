from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from django.contrib.auth import login
from .models import Tour, Reservation, Review, Country
from .forms import ReservationForm, ReviewForm, TourForm, ToursRegisterForm



class TourListView(ListView):
    model = Tour
    template_name = 'tours/tour_list.html'
    context_object_name = 'tours'
    paginate_by = 6

    def get_queryset(self):
        qs = Tour.objects.select_related('country', 'agency')

        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

        country = self.request.GET.get('country')
        if country and country.isdigit() and int(country) > 0:
            qs = qs.filter(country_id=int(country))

        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                qs = qs.filter(price__lte=float(max_price))
            except ValueError:
                pass

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['current_q'] = self.request.GET.get('q', '')
        ctx['current_max_price'] = self.request.GET.get('max_price', '')

        current_country_raw = self.request.GET.get('country', '')
        current_country_id = int(current_country_raw) if current_country_raw.isdigit() else 0
        ctx['current_country_id'] = current_country_id

        countries_qs = Country.objects.all()
        ctx['countries'] = [
            {'id': c.id, 'name': c.name, 'is_selected': (c.id == current_country_id)}
            for c in countries_qs
        ]

        return ctx


class TourDetailView(DetailView):
    model = Tour
    template_name = 'tours/tour_detail.html'
    context_object_name = 'tour'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['reviews'] = self.object.reviews.select_related('user')
        ctx['reservation_form'] = ReservationForm()
        ctx['review_form'] = ReviewForm()
        ctx['user_reservation'] = None
        ctx['user_review'] = None

        if self.request.user.is_authenticated:
            ctx['user_reservation'] = Reservation.objects.filter(
                user=self.request.user, tour=self.object
            ).exclude(status='cancelled').first()

            ctx['user_review'] = Review.objects.filter(
                user=self.request.user, tour=self.object
            ).first()
        return ctx


@login_required
def reserve_tour(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.method == 'POST':
        existing = Reservation.objects.filter(
            user=request.user, tour=tour
        ).exclude(status='cancelled').first()

        if existing:
            messages.warning(request, 'У вас уже есть резервирование этого тура.')
            return redirect('tour_detail', pk=pk)

        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.tour = tour

            if reservation.participants_count > tour.available_slots:
                messages.error(request, 'Недостаточно свободных мест.')
                return redirect('tour_detail', pk=pk)

            reservation.save()
            messages.success(request, 'Тур зарезервирован! Ожидайте подтверждения.')
            return redirect('reservation_list')

    return redirect('tour_detail', pk=pk)


class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'tours/reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 10

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user
        ).select_related('tour', 'tour__country')


class ReservationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reservation
    fields = ('participants_count',)
    template_name = 'tours/reservation_form.html'
    success_url = reverse_lazy('reservation_list')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user and obj.status == 'pending'


class ReservationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reservation
    template_name = 'tours/reservation_confirm_delete.html'
    success_url = reverse_lazy('reservation_list')

    def test_func(self):
        return self.get_object().user == self.request.user



@login_required
def add_review(request, pk):
    tour = get_object_or_404(Tour, pk=pk)

    if request.method == 'POST':
        has_reservation = Reservation.objects.filter(
            user=request.user, tour=tour, status='confirmed'
        ).exists()

        if not has_reservation:
            messages.error(
                request,
                'Оставить отзыв можно только после подтверждённого резервирования.'
            )
            return redirect('tour_detail', pk=pk)

        existing = Review.objects.filter(user=request.user, tour=tour).first()
        if existing:
            messages.warning(request, 'Вы уже оставили отзыв к этому туру.')
            return redirect('tour_detail', pk=pk)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.tour = tour
            review.save()
            messages.success(request, 'Отзыв добавлен!')

    return redirect('tour_detail', pk=pk)



class TourCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Tour
    form_class = TourForm
    template_name = 'tours/tour_form.html'
    success_url = reverse_lazy('tour_list')

    def test_func(self):
        return self.request.user.is_staff


class TourUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Tour
    form_class = TourForm
    template_name = 'tours/tour_form.html'
    success_url = reverse_lazy('tour_list')

    def test_func(self):
        return self.request.user.is_staff


class TourDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tour
    template_name = 'tours/tour_confirm_delete.html'
    success_url = reverse_lazy('tour_list')

    def test_func(self):
        return self.request.user.is_staff


class SoldToursByCountryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'tours/sold_tours.html'
    context_object_name = 'countries'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Country.objects.annotate(
            sold_count=Count(
                'tours__reservations',
                filter=Q(tours__reservations__status='confirmed')
            )
        ).filter(sold_count__gt=0).order_by('-sold_count')
    

def register_tours(request):
    if request.method == 'POST':
        form = ToursRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tour_list')
    else:
        form = ToursRegisterForm()

    return render(request, 'tours/register.html', {
        'form': form,
        'title': 'Регистрация',
    })

@login_required
def profile_tours(request):
    reservations = Reservation.objects.filter(user=request.user).select_related('tour', 'tour__country')
    return render(request, 'tours/profile.html', {
        'reservations': reservations,
    })