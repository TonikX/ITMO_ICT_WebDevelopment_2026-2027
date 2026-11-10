from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, UserForm
from .models import Car, User


def owner_detail(request, owner_id):
    try:
        owner = User.objects.get(pk=owner_id)
    except User.DoesNotExist:
        raise Http404("Owner does not exist")
    return render(request, "owner.html", {"owner": owner})


def owner_list(request):
    context = {}
    context["dataset"] = User.objects.all()
    return render(request, "owners.html", context)


def owner_create(request):
    context = {}
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("/owners/")
    context["form"] = form
    return render(request, "owner_form.html", context)


class CarListView(ListView):
    model = Car
    template_name = "cars.html"


class CarDetailView(DetailView):
    model = Car
    template_name = "car_detail.html"


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = "/cars/"


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = "/cars/"


class CarDeleteView(DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    success_url = "/cars/"
