
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import OwnerForm
from .models import Car, Owner

def get_all_owners(request):
    dataset = Owner.objects.all()
    return render(request, 'owners.html', {'dataset': dataset})

def owner(request, pk):
    owner_obj = get_object_or_404(Owner, pk=pk)
    context = {
        'owner': owner_obj,
        'ownerships': owner_obj.ownerships.select_related('car'),
    }
    return render(request, 'owner.html', context)

class CarListView(ListView):

    model = Car
    template_name = 'car_list.html'
    ordering = ('brand', 'model')

class CarDetailView(DetailView):

    model = Car
    template_name = 'car_detail.html'

class CarUpdateView(UpdateView):

    model = Car
    template_name = 'car_form.html'
    fields = ['brand', 'model', 'color', 'state_number']
    success_url = reverse_lazy('car_list')

def create_owner(request):
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owners_list')
    else:
        form = OwnerForm()
    return render(request, 'create_owner.html', {'form': form})

class CarCreateView(CreateView):

    model = Car
    template_name = 'car_form.html'
    fields = ['brand', 'model', 'color', 'state_number']
    success_url = reverse_lazy('car_list')

class CarDeleteView(DeleteView):

    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
