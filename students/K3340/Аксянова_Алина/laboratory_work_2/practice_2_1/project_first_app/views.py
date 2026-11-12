from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import CarOwner, Car
from .forms import CarOwnerForm


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})


def owner_list(request):
    owners = CarOwner.objects.all()
    return render(request, 'owner_list.html', {'owners': owners})


def owner_create(request):
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = CarOwnerForm()

    return render(request, 'owner_form.html', {'form': form})


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'


class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'


class CarCreateView(CreateView):
    model = Car
    fields = ['plate_number', 'brand', 'model_name', 'color']
    template_name = 'car_form.html'
    success_url = reverse_lazy('car_list')


class CarUpdateView(UpdateView):
    model = Car
    fields = ['plate_number', 'brand', 'model_name', 'color']
    template_name = 'car_form.html'
    success_url = reverse_lazy('car_list')

class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
