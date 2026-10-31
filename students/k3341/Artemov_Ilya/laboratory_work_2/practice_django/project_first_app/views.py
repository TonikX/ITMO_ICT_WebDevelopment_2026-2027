from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import CarForm, OwnerCreationForm
from .models import Car, CarOwner


def owner_list(request):
    return render(request, "owners.html", {"owners": CarOwner.objects.all()})


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, "owner.html", {
        "owner": owner, "ownerships": owner.ownerships.select_related("car"),
    })


def owner_create(request):
    form = OwnerCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        owner = form.save()
        return redirect("owner", owner_id=owner.pk)
    return render(request, "form.html", {"form": form, "title": "Создание пользователя-владельца"})


class CarListView(ListView):
    model = Car
    template_name = "cars.html"
    context_object_name = "cars"


class CarDetailView(DetailView):
    model = Car
    template_name = "car.html"


class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = "form.html"
    success_url = reverse_lazy("cars")
    extra_context = {"title": "Добавление автомобиля"}


class CarUpdateView(LoginRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = "form.html"
    success_url = reverse_lazy("cars")
    extra_context = {"title": "Редактирование автомобиля"}


class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = reverse_lazy("cars")
