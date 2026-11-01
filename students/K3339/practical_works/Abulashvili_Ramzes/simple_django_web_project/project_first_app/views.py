from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, OwnerForm
from .models import Car, CarOwner


def owner_list(request):
    owners = CarOwner.objects.prefetch_related("cars")
    return render(request, "owners.html", {"owners": owners})


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    periods = owner.ownership_set.select_related("car")
    return render(request, "owner.html", {"owner": owner, "periods": periods})


def owner_create(request):
    form = OwnerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        owner = form.save()
        return redirect("owner_detail", owner_id=owner.pk)
    return render(request, "form.html", {"form": form, "title": "Новый автовладелец"})


class CarListView(ListView):
    model = Car
    template_name = "cars.html"
    context_object_name = "cars"


class CarDetailView(DetailView):
    model = Car
    template_name = "car.html"
    context_object_name = "car"


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = "form.html"
    success_url = reverse_lazy("cars")
    extra_context = {"title": "Новый автомобиль"}


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = "form.html"
    success_url = reverse_lazy("cars")
    extra_context = {"title": "Редактирование автомобиля"}


class CarDeleteView(DeleteView):
    model = Car
    template_name = "car_delete.html"
    success_url = reverse_lazy("cars")
