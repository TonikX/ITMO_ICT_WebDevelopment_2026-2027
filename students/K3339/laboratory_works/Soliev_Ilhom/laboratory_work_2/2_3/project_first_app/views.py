from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .forms import CarOwnerCreationForm
from .models import Car, User


def owner_detail(request, owner_id):
    owner = get_object_or_404(User, pk=owner_id)
    return render(request, "owner.html", {"owner": owner})


def owner_list(request):
    owners = User.objects.all().order_by("last_name", "first_name", "username")
    return render(request, "owner_list.html", {"owners": owners})


def owner_create(request):
    if request.method == "POST":
        form = CarOwnerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("owner_list")
    else:
        form = CarOwnerCreationForm()

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
    fields = ["registration_number", "brand", "model", "color"]
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


class CarCreateView(CreateView):
    model = Car
    fields = ["registration_number", "brand", "model", "color"]
    template_name = "car_form.html"
    success_url = reverse_lazy("car_list")


class CarDeleteView(DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = reverse_lazy("car_list")
