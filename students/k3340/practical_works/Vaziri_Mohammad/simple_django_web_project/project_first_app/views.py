from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, OwnerCreationForm
from .models import Car, Owner


# ---------- Практика 2.1: владелец по id (функциональное представление) ----------
def owner_detail(request, owner_id):
    try:
        owner = Owner.objects.get(pk=owner_id)
    except Owner.DoesNotExist:
        raise Http404("Owner does not exist")
    ownerships = owner.ownerships.select_related("car").order_by("start_date")
    return render(request, "owner.html", {"owner": owner, "ownerships": ownerships})


# ---------- Практика 2.2: все владельцы (функционально) ----------
def owner_list(request):
    context = {"owners": Owner.objects.filter(is_staff=False).prefetch_related("cars").order_by("last_name", "first_name")}
    return render(request, "owners_list.html", context)


# ---------- Практики 2.2–2.3: форма ввода владельца = создание пользователя ----------
def owner_create(request):
    form = OwnerCreationForm(request.POST or None)
    if form.is_valid():
        owner = form.save()
        return redirect("owner_detail", owner_id=owner.pk)
    return render(request, "owner_form.html", {"form": form})


# ---------- Практика 2.2: автомобили на основе классов ----------
class CarListView(ListView):
    model = Car
    template_name = "project_first_app/car_list.html"


class CarDetailView(DetailView):
    model = Car
    template_name = "project_first_app/car_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ownerships"] = self.object.ownerships.select_related("owner").order_by("start_date")
        return context


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = "project_first_app/car_form.html"
    success_url = reverse_lazy("car_list")


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = "project_first_app/car_form.html"
    success_url = reverse_lazy("car_list")


class CarDeleteView(DeleteView):
    model = Car
    template_name = "project_first_app/car_confirm_delete.html"
    success_url = reverse_lazy("car_list")
