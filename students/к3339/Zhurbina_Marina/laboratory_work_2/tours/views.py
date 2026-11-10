from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, DecimalField, F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import FormMixin

from .forms import ReviewForm
from .models import Agency, Reservation, Review, Tour


class TourListView(ListView):
    model = Tour
    template_name = 'tours/tour_list.html'
    context_object_name = 'tours'
    paginate_by = 5

    def get_queryset(self):
        queryset = Tour.objects.select_related('agency').order_by('date_start')
        country = self.request.GET.get('country')
        agency_id = self.request.GET.get('agency')
        search = self.request.GET.get('q')
        if country:
            queryset = queryset.filter(country=country)
        if agency_id:
            queryset = queryset.filter(agency_id=agency_id)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = (
            Tour.objects.order_by('country').values_list('country', flat=True).distinct()
        )
        context['agencies'] = Agency.objects.all()
        params = self.request.GET.copy()
        params.pop('page', None)
        context['querystring'] = params.urlencode()
        return context


class TourDetailView(FormMixin, DetailView):
    model = Tour
    template_name = 'tours/tour_detail.html'
    context_object_name = 'tour'
    form_class = ReviewForm

    def get_success_url(self):
        return reverse('tour_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.select_related(
            'author',
        ).order_by('-created_at')
        if self.request.user.is_authenticated:
            context['my_reservation'] = self.object.reservations.filter(
                user=self.request.user,
            ).first()
            context['my_review'] = self.object.reviews.filter(
                author=self.request.user,
            ).first()
        if self.request.user.is_staff:
            context['tour_reservations'] = self.object.reservations.select_related(
                'user',
            ).order_by('-created_at')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.author = self.request.user
        review.tour = self.object
        review.tour_date_start = self.object.date_start
        review.tour_date_end = self.object.date_end
        review.save()
        return super().form_valid(form)


class MyReservationsView(LoginRequiredMixin, ListView):
    template_name = 'tours/my_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user,
        ).select_related('tour', 'tour__agency').order_by('-created_at')


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    template_name = 'tours/reservation_form.html'
    fields = ['guests']
    success_url = reverse_lazy('my_reservations')

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'tours/reservation_confirm_delete.html'
    success_url = reverse_lazy('my_reservations')

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'tours/register.html', {'form': form})


@login_required
def tour_reserve(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    if request.method == 'POST':
        Reservation.objects.get_or_create(user=request.user, tour=tour)
    return redirect('tour_detail', pk=pk)


def sales(request):
    rows = (
        Reservation.objects.filter(status='confirmed')
        .values(country=F('tour__country'))
        .annotate(
            tours_sold=Count('id'),
            tourists=Sum('guests'),
            revenue=Sum(
                F('tour__price') * F('guests'),
                output_field=DecimalField(),
            ),
        )
        .order_by('-revenue')
    )
    context = {'rows': rows}
    if request.user.is_staff:
        context['pending_count'] = Reservation.objects.filter(
            status='pending',
        ).count()
    return render(request, 'tours/sales.html', context)
