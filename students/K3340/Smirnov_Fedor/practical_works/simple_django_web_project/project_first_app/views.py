from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, OwnerForm
from .models import Car, CarOwner


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    ownerships = owner.ownership_set.select_related('car')
    return render(request, 'owner.html', {'owner': owner, 'ownerships': ownerships})


def owner_list(request):
    owners = CarOwner.objects.order_by('id')
    return render(request, 'owner_list.html', {'owners': owners})


def owner_create(request):
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            owner = form.save()
            return redirect('owner_detail', owner_id=owner.pk)
    else:
        form = OwnerForm()
    return render(request, 'owner_form.html', {'form': form})


class CarList(ListView):
    model = Car
    template_name = 'car_list.html'


class CarDetail(DetailView):
    model = Car
    template_name = 'car_detail.html'


class CarCreate(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'car_form.html'
    success_url = reverse_lazy('car_list')


class CarUpdate(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'car_form.html'
    success_url = reverse_lazy('car_list')


class CarDelete(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
