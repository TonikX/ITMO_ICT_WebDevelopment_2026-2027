from django.shortcuts import render, get_object_or_404
from .models import Driver


def owner_info(request, owner_id):
    owner = get_object_or_404(Driver, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})

