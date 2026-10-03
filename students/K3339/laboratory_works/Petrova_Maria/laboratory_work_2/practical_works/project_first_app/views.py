from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, CarOwnerForm
from .models import Car

CarOwner = get_user_model()


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, "owner.html", {"owner": owner})


def owner_list(request):
    owners = CarOwner.objects.all().order_by("id")
    return render(request, "owner_list.html", {"owners": owners})


def owner_create(request):
    if request.method == "POST":
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            owner = form.save()
            return redirect("owner_detail", owner_id=owner.id)
    else:
        form = CarOwnerForm()
    return render(request, "owner_form.html", {"form": form})


class CarListView(ListView):
    model = Car
    template_name = "car_list.html"
    context_object_name = "cars"
    ordering = ["id"]


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"
    context_object_name = "car"


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


class CarDeleteView(DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = reverse_lazy("car_list")
