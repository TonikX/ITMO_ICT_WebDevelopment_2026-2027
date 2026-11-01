from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from .models import CarOwner, Car
from .forms import OwnerCreationForm


# практика 2.1
def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})



# практика 2.2
# вывод списка всех владельцев (FBV)
def owner_list(request):
    owners = CarOwner.objects.all()
    return render(request, 'owner_list.html', {'owners': owners})

# вывод списка всех автомобилей (CBV)
class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'

# вывод конкретного автомобиля по ID (CBV)
class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'

# обновление данных автомобиля (CBV)
class CarUpdateView(UpdateView):
    model = Car
    fields = ['state_number', 'brand', 'model_name', 'color']
    template_name = 'car_update.html'
    success_url = '/cars/'


# создание владельца через форму (FBV)
def owner_create(request):
    if request.method == 'POST':
        form = OwnerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = OwnerCreationForm()
    return render(request, 'owner_create.html', {'form': form})

# создание автомобиля (CBV)
class CarCreateView(CreateView):
    model = Car
    fields = ['state_number', 'brand', 'model_name', 'color']
    template_name = 'car_create.html'
    success_url = reverse_lazy('car_list')

# удаление автомобиля (CBV)
class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')