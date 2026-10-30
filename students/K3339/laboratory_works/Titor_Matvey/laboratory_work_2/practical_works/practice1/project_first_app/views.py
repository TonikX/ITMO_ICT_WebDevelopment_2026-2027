
from django.shortcuts import get_object_or_404, render

from .models import Owner

def owner(request, pk):
    owner_obj = get_object_or_404(Owner, pk=pk)
    context = {
        'owner': owner_obj,
        'ownerships': owner_obj.ownerships.select_related('car'),
    }
    return render(request, 'owner.html', context)
