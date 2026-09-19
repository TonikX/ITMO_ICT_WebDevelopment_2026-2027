from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import CarOwnerForm
from .models import Car, CarOwner


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, "owner.html", {"owner": owner})


def owners_list(request):
    context = {"owners": CarOwner.objects.all()}
    return render(request, "owners_list.html", context)


def owner_create(request):
    if request.method == "POST":
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("owners_list")
    else:
        form = CarOwnerForm()
    return render(request, "owner_form.html", {"form": form})


class CarListView(ListView):
    model = Car
    template_name = "car_list.html"
    context_object_name = "cars"


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"
    context_object_name = "car"


class CarUpdateView(UpdateView):
    model = Car
    fields = ["license_plate", "brand", "model", "color"]
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


class CarCreateView(CreateView):
    model = Car
    fields = ["license_plate", "brand", "model", "color"]
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


class CarDeleteView(DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = reverse_lazy("car_list")
