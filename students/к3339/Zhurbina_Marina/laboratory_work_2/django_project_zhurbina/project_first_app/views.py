from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import UserCreateForm
from .models import Car

User = get_user_model()


def owner_detail(request, owner_id):
    try:
        owner = User.objects.get(pk=owner_id)
    except User.DoesNotExist:
        raise Http404('Владелец не найден')
    return render(request, 'owner.html', {'owner': owner})


def owners_list(request):
    owners = User.objects.all()
    return render(request, 'owners.html', {'owners': owners})


def owner_create(request):
    form = UserCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('owners_list')
    return render(request, 'owner_create.html', {'form': form})


class CarListView(ListView):
    model = Car
    template_name = 'cars_list.html'
    context_object_name = 'cars'


class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'car'


class CarUpdateView(UpdateView):
    model = Car
    template_name = 'car_form.html'
    fields = ['plate_number', 'brand', 'car_model', 'color']
    success_url = reverse_lazy('cars_list')


class CarCreateView(CreateView):
    model = Car
    template_name = 'car_form.html'
    fields = ['plate_number', 'brand', 'car_model', 'color']
    success_url = reverse_lazy('cars_list')


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('cars_list')
