from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, CarOwnerCreateForm
from .models import Car, CarOwner


def home(request):
    return render(request, 'home.html')


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})


def owner_list(request):
    owners = CarOwner.objects.order_by('last_name', 'first_name')
    return render(request, 'owner_list.html', {'owners': owners})


def owner_create(request):
    form = CarOwnerCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        owner = form.save()
        return redirect('owner_detail', owner_id=owner.pk)
    return render(request, 'owner_form.html', {'form': form})


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        return Car.objects.order_by('brand', 'model_name')


class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'car'


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'car_form.html'
    success_url = reverse_lazy('car_list')


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'car_form.html'

    def get_success_url(self):
        return reverse_lazy('car_detail', kwargs={'pk': self.object.pk})


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
    context_object_name = 'car'
