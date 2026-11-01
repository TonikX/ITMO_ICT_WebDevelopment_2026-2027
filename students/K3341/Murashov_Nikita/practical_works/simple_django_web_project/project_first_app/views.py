from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, CarOwnerForm
from .models import Car, CarOwner


# Практика 1, задание 4: владелец по идентификатору (FBV).
def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    ownerships = owner.ownerships.select_related("car")
    return render(request, "owner.html", {"owner": owner, "ownerships": ownerships, "licenses": owner.licenses.all()})


# Практика 2, задание 2.1: все владельцы (FBV).
def owner_list(request):
    return render(request, "owners.html", {"owners": CarOwner.objects.order_by("last_name", "username")})


# Практика 3, задание 1: форма ввода владельца (FBV).
def owner_create(request):
    form = CarOwnerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        owner = form.save()
        return redirect("owner_detail", owner_id=owner.pk)
    return render(request, "owner_form.html", {"form": form})


# Практика 2, задание 2.2: автомобили на классах.
class CarListView(ListView):
    model = Car
    template_name = "car_list.html"
    context_object_name = "cars"

    def get_queryset(self):
        qs = super().get_queryset()
        brand = self.request.GET.get("brand")
        return qs.filter(brand__iexact=brand) if brand else qs


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


# Практика 3, задание 2: создание и удаление автомобиля (CBV).
class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


class CarDeleteView(DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = reverse_lazy("car_list")
