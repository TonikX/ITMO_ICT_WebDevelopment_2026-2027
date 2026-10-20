from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import CarOwnerCreationForm, CarOwnerForm
from .models import Car, CarOwner


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})


def owner_list(request):
    context = {'owners': CarOwner.objects.all()}
    return render(request, 'owner_list.html', context)


def owner_create(request):
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = CarOwnerForm()
    return render(request, 'owner_create.html', {'form': form})


def owner_register(request):
    if request.method == 'POST':
        form = CarOwnerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = CarOwnerCreationForm()
    return render(request, 'owner_register.html', {'form': form})


class CarListView(ListView):
    model = Car


class CarDetailView(DetailView):
    model = Car


class CarCreateView(CreateView):
    model = Car
    fields = ['plate_number', 'brand', 'model', 'color']
    success_url = reverse_lazy('car_list')


class CarUpdateView(UpdateView):
    model = Car
    fields = ['plate_number', 'brand', 'model', 'color']
    success_url = reverse_lazy('car_list')


class CarDeleteView(DeleteView):
    model = Car
    success_url = reverse_lazy('car_list')
