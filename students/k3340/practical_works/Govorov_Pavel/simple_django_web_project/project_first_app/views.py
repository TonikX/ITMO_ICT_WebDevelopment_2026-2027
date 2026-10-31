from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CarForm, OwnerForm
from .models import Car, Owner


def owner_list(request):
    return render(request, "owners.html", {"owners": Owner.objects.all()})


def owner_detail(request, pk):
    owner = get_object_or_404(Owner, pk=pk)
    return render(
        request,
        "owner.html",
        {"owner": owner, "ownerships": owner.ownership_set.select_related("car")},
    )


def owner_create(request):
    form = OwnerForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("car_list")
    return render(request, "form.html", {"form": form, "title": "Создать пользователя"})


class CarList(ListView):
    model = Car
    template_name = "cars.html"
    context_object_name = "cars"


class CarDetail(DetailView):
    model = Car
    template_name = "car.html"


class CarCreate(CreateView):
    model = Car
    form_class = CarForm
    template_name = "form.html"
    success_url = reverse_lazy("car_list")
    extra_context = {"title": "Добавить автомобиль"}


class CarUpdate(UpdateView):
    model = Car
    form_class = CarForm
    template_name = "form.html"
    success_url = reverse_lazy("car_list")
    extra_context = {"title": "Изменить автомобиль"}


class CarDelete(DeleteView):
    model = Car
    template_name = "delete.html"
    success_url = reverse_lazy("car_list")
