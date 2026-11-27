
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, UpdateView,
    CreateView, DeleteView
)
from django.urls import reverse_lazy
from .models import User, Car
from .forms import UserForm


def user_list(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})


def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()

    return render(request, 'user_form.html', {'form': form})


class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'


class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'car'
    pk_url_kwarg = 'car_id'


class CarCreateView(CreateView):
    model = Car
    fields = ['car_number', 'brand', 'model', 'color']
    template_name = 'car_form.html'
    success_url = reverse_lazy('car_list')


class CarUpdateView(UpdateView):
    model = Car
    fields = ['car_number', 'brand', 'model', 'color']
    template_name = 'car_form.html'
    pk_url_kwarg = 'car_id'
    success_url = reverse_lazy('car_list')


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    pk_url_kwarg = 'car_id'
    success_url = reverse_lazy('car_list')
