from django.shortcuts import render, get_object_or_404, redirect
from .models import CarOwner, Car
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from .forms import OwnerForm, RegisterForm
from django.urls import reverse_lazy

def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})

def owner_list(request):
    owners = CarOwner.objects.all()
    return render(request, 'owner_list.html', {'owners': owners})

class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'

class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'car'

class CarUpdateView(UpdateView):
    model = Car
    fields = ['plate_number', 'brand', 'model_name', 'color']
    template_name = 'car_update.html'
    success_url = '/cars/'

def owner_create(request):
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = OwnerForm()
    return render(request, 'owner_create.html', {'form': form})

class CarCreateView(CreateView):
    model = Car
    fields = ['plate_number', 'brand', 'model_name', 'color']
    template_name = 'car_create.html'
    success_url = '/cars/'


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})