from django.shortcuts import render, get_object_or_404
from .models import CarOwner
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from .models import Car
from django import forms
from django.shortcuts import redirect

from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect


# ... остальные импорты ...

def user_list(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def user_create(request):
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        passport = request.POST.get('passport_number')
        address = request.POST.get('home_address')
        nationality = request.POST.get('nationality')

        if username and password:
            User.objects.create_user(
                username=username,
                password=password,
                name=name,
                passport_number=passport,
                home_address=address,
                nationality=nationality
            )
            return redirect('user_list')

    return render(request, 'user_create.html')

def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})

def owner_list(request):
    owners = CarOwner.objects.all()
    return render(request, 'owner_list.html', {'owners': owners})


class CarList(ListView):
    model = Car
    template_name = 'car_list.html'

class CarDetail(DetailView):
    model = Car
    template_name = 'car_detail.html'

class CarUpdate(UpdateView):
    model = Car
    fields = ['brand', 'model_name', 'state_number', 'color']
    template_name = 'car_update.html'
    success_url = reverse_lazy('car_list')

class CarOwnerForm(forms.ModelForm):
    class Meta:
        model = CarOwner
        fields = ['first_name', 'last_name', 'birth_date']

def owner_create(request):
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = CarOwnerForm()
    return render(request, 'owner_create.html', {'form': form})


class CarCreate(CreateView):
    model = Car
    fields = ['brand', 'model_name', 'state_number', 'color']
    template_name = 'car_create.html'
    success_url = reverse_lazy('car_list')

class CarDelete(DeleteView):
    model = Car
    template_name = 'car_delete.html'
    success_url = reverse_lazy('car_list')