from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import OwnerForm, CarForm
from .models import Owner, Car


def owner_list(request):
    owners = Owner.objects.all()
    return render(request, 'owners.html', {'owners': owners})


def owner_detail(request, pk):
    owner = get_object_or_404(Owner, pk=pk)
    return render(request, 'owner.html', {'owner': owner})


def owner_create(request):
    form = OwnerForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'created.html')
    return render(request, 'form.html', {'form': form, 'title': 'Создание владельца'})


class CarListView(ListView):
    model = Car
    template_name = 'cars.html'


class CarDetailView(DetailView):
    model = Car
    template_name = 'car.html'


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'form.html'
    success_url = reverse_lazy('car_list')
    extra_context = {'title': 'Создание автомобиля'}


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'form.html'
    success_url = reverse_lazy('car_list')
    extra_context = {'title': 'Изменение автомобиля'}


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'delete.html'
    success_url = reverse_lazy('car_list')
