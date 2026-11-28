from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Flight, Reservation, Review
from .forms import UserRegisterForm, ReviewForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('flight_list')
    else:
        form = UserRegisterForm()
    return render(request, 'flights/register.html', {'form': form})


class FlightListView(ListView):
    model = Flight
    template_name = 'flights/flight_list.html'
    context_object_name = 'flights'
    paginate_by = 5

    def get_queryset(self):
        qs = Flight.objects.select_related('airline')
        search = self.request.GET.get('search')
        ftype = self.request.GET.get('type')
        if search:
            qs = qs.filter(number__icontains=search)
        if ftype:
            qs = qs.filter(flight_type=ftype)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx['my_reservations'] = Reservation.objects.filter(user=self.request.user).values_list('flight_id', flat=True)
        return ctx


class FlightDetailView(DetailView):
    model = Flight
    template_name = 'flights/flight_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['passengers'] = Reservation.objects.filter(flight=self.object).select_related('user')
        ctx['reviews'] = self.object.review_set.select_related('user').all()
        ctx['review_form'] = ReviewForm()
        if self.request.user.is_authenticated:
            ctx['my_reservations'] = list(
                Reservation.objects.filter(user=self.request.user).values_list('flight_id', flat=True)
            )
        else:
            ctx['my_reservations'] = []
        return ctx

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    fields = []
    template_name = 'flights/reservation_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['flight'] = get_object_or_404(Flight, pk=self.kwargs['pk'])
        return ctx

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.flight = get_object_or_404(Flight, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('flight_detail', kwargs={'pk': self.kwargs['pk']})

class ReservationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reservation
    fields = []
    template_name = 'flights/reservation_form.html'

    def test_func(self):
        return self.get_object().user == self.request.user or self.request.user.is_staff

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['flight'] = self.object.flight
        return ctx

    def get_success_url(self):
        return reverse_lazy('flight_detail', kwargs={'pk': self.object.flight.pk})


class ReservationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reservation
    template_name = 'flights/reservation_confirm_delete.html'

    def test_func(self):
        return self.get_object().user == self.request.user or self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('flight_detail', kwargs={'pk': self.object.flight.pk})


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'flights/review_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.flight = get_object_or_404(Flight, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('flight_detail', kwargs={'pk': self.kwargs['pk']})
