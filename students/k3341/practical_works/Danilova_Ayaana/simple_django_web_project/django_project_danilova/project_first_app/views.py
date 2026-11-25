from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import User, Car
from .forms import UserForm, CarForm

# Create your views here.


def owner_detail(request, owner_id):
    owner = get_object_or_404(User, pk=owner_id)
    return render(request, 'owner.html', {'driver': owner})


def drivers_info(request):
    context = {}
    context['drivers'] = User.objects.all()
    return render(request, 'drivers.html', context)


class CarSingleView(DetailView):
    model = Car
    template_name = 'car_detail.html'


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'


class CarUpdateView(UpdateView):
    model = Car
    fields = ['number', 'brand', 'model', 'color']
    template_name = 'car_update.html'
    success_url = reverse_lazy('car_list')


def create_driver(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('driver_list')
    else:
        form = UserForm()
    return render(request, 'driver_form.html', {'form': form})


class CarCreateForm(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'car_create_form.html'
    success_url = reverse_lazy('car_list')


class CarUpdateForm(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'car_update_form.html'
    success_url = reverse_lazy('car_list')


class CarDeleteForm(DeleteView):
    model = Car
    template_name = 'car_delete_form.html'
    success_url = reverse_lazy('car_list')







