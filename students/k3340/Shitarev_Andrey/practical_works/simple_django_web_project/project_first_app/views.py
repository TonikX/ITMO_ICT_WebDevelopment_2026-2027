from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import OwnerForm, CarForm
from .models import Owner, Car


def owner_detail(request, owner_id):
    owner = get_object_or_404(Owner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner}, using='jinja2')


def owner_list(request):
    return render(request, 'owners.html', {'owners': Owner.objects.all()}, using='jinja2')


def owner_create(request):
    form = OwnerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('owner_list')
    return render(request, 'form.html', {'form': form}, using='jinja2')


class CarList(ListView):
    model = Car
    template_name = 'cars.html'
    template_engine = 'jinja2'


class CarDetail(DetailView):
    model = Car
    template_name = 'car.html'
    template_engine = 'jinja2'


class CarCreate(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'form.html'
    template_engine = 'jinja2'
    success_url = reverse_lazy('car_list')


class CarUpdate(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'form.html'
    template_engine = 'jinja2'
    success_url = reverse_lazy('car_list')


class CarDelete(DeleteView):
    model = Car
    template_name = 'car_delete.html'
    template_engine = 'jinja2'
    success_url = reverse_lazy('car_list')
