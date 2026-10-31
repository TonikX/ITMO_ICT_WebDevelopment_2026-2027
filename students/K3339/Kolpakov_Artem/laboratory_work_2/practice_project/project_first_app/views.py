from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, RegistrationForm
from .models import Car, User


def owner_list(request):
    owners = User.objects.prefetch_related("driver_licenses", "ownerships__car")
    return render(request, "project_first_app/owner_list.html", {"owners": owners})


def owner_detail(request, owner_id):
    owner = get_object_or_404(
        User.objects.prefetch_related("driver_licenses", "ownerships__car"),
        pk=owner_id,
    )
    return render(request, "project_first_app/owner_detail.html", {"owner": owner})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("owner_list")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


class CarListView(ListView):
    model = Car
    template_name = "project_first_app/car_list.html"
    context_object_name = "cars"


class CarDetailView(DetailView):
    model = Car
    template_name = "project_first_app/car_detail.html"
    context_object_name = "car"


class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = "project_first_app/car_form.html"
    success_url = reverse_lazy("car_list")


class CarUpdateView(LoginRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = "project_first_app/car_form.html"
    success_url = reverse_lazy("car_list")


class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = "project_first_app/car_confirm_delete.html"
    success_url = reverse_lazy("car_list")
