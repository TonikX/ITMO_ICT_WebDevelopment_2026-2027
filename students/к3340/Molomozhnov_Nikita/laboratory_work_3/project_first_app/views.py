from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import CarOwner, Car
from .forms import CarOwnerForm, UserForm
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import (
    CarOwnerSerializer,
    CarOwnerFullSerializer,
    CarSerializer,
    CarFullSerializer,
    OwnershipSerializer,
)
User = get_user_model()


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


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


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


class CarCreateView(CreateView):
    model = Car
    template_name = 'car_form.html'
    fields = ['state_number', 'brand', 'model_name', 'color']
    success_url = reverse_lazy('car_list')


class CarUpdateView(UpdateView):
    model = Car
    template_name = 'car_form.html'
    fields = ['state_number', 'brand', 'model_name', 'color']
    success_url = reverse_lazy('car_list')


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')

class CarOwnerListCreateView(generics.ListCreateAPIView):
    queryset = CarOwner.objects.all()
    serializer_class = CarOwnerSerializer


class CarOwnerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarOwner.objects.all()
    serializer_class = CarOwnerFullSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CarListCreateView(generics.ListCreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarFullSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class OwnershipListCreateView(generics.ListCreateAPIView):
    queryset = Ownership.objects.all()
    serializer_class = OwnershipSerializer