from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import CarOwnerForm
from django.urls import reverse_lazy
from project_first_app.models import User, Car


# Create your views here.

def owner_detail(request, owner_id):
    owner = get_object_or_404(User, pk=owner_id)
    return render(request, 'owners/owner.html', {'owner': owner})


def owners_list(request):
    owners = User.objects.all()
    return render(request, 'owners/owners.html', {'owners': owners})


class CarListView(ListView):
    model = Car
    template_name = 'cars/cars_list.html'


class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car_detail.html'


# задание 3
def create_owner(request):
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()  # создает или обновляет объект данных
            return redirect('owners_list')
    else:
        form = CarOwnerForm()
    return render(request, 'owners/create_owner.html', {'form': form})


def owner_update(request, pk):
    owner = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CarOwnerForm(request.POST, instance=owner)
        if form.is_valid():
            form.save()
            return redirect('owners_list')
    else:
        form = CarOwnerForm(instance=owner)
    return render(request, 'owners/create_owner.html', {'form': form, 'title': 'Редактировать владельца'})


# Удаление (FBV)
def owner_delete(request, pk):
    owner = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        owner.delete()
        return redirect('owners_list')
    return render(request, 'owners/owner_confirm_delete.html', {'owner': owner})

# CBV обновление

class CarUpdateView(UpdateView):
    model = Car
    fields = ['license_plate', 'brand', 'model', 'color']
    template_name = 'cars/update_car.html'
    success_url = '/cars'

class CarCreate(CreateView):
    model = Car
    fields = ['license_plate', 'brand', 'model', 'color']
    template_name = 'cars/create_car.html'
    success_url = '/cars'

class CarDelete(DeleteView):
    model = Car
    template_name = 'cars/car_confirm_delete.html'
    success_url = reverse_lazy('cars_list')

