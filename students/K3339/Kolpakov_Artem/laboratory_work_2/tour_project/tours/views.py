from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import RegistrationForm, ReservationForm, ReviewForm
from .models import Country, Reservation, Review, Tour


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("tour_list")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


class TourListView(ListView):
    model = Tour
    template_name = "tours/tour_list.html"
    context_object_name = "tours"
    paginate_by = 5

    def get_queryset(self):
        tours = Tour.objects.select_related("agency", "country")
        query = self.request.GET.get("q", "")
        country = self.request.GET.get("country", "")

        if query:
            tours = tours.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        if country:
            tours = tours.filter(country_id=country)

        return tours

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()
        context["query"] = self.request.GET.get("q", "")
        context["selected_country"] = self.request.GET.get("country", "")
        return context


class TourDetailView(DetailView):
    model = Tour
    template_name = "tours/tour_detail.html"
    context_object_name = "tour"

    def get_queryset(self):
        return Tour.objects.select_related("agency", "country").prefetch_related(
            "reviews__user"
        )


@login_required
@require_POST
def reserve_tour(request, tour_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    Reservation.objects.create(user=request.user, tour=tour)
    return redirect("reservation_list")


class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "tours/reservation_list.html"
    context_object_name = "reservations"

    def get_queryset(self):
        reservations = Reservation.objects.select_related(
            "user", "tour", "tour__country"
        )
        if self.request.user.is_staff:
            return reservations
        return reservations.filter(user=self.request.user)


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = "tours/reservation_form.html"
    success_url = reverse_lazy("reservation_list")

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class ReservationDeleteView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = "tours/reservation_confirm_delete.html"
    success_url = reverse_lazy("reservation_list")

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "tours/review_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.tour = get_object_or_404(Tour, pk=kwargs["tour_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.tour = self.tour
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tour"] = self.tour
        return context

    def get_success_url(self):
        return reverse("tour_detail", args=[self.tour.pk])


@user_passes_test(lambda user: user.is_staff)
@require_POST
def confirm_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.is_confirmed = True
    reservation.save()
    return redirect("reservation_list")


class SoldTourListView(ListView):
    model = Reservation
    template_name = "tours/sold_tour_list.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return (
            Reservation.objects.filter(is_confirmed=True)
            .select_related("user", "tour", "tour__country", "tour__agency")
            .order_by("tour__country__name", "tour__start_date")
        )
