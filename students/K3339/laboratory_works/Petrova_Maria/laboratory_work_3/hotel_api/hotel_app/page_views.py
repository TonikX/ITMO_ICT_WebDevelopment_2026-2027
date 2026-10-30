from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.http import require_GET


@staff_member_required
@require_GET
def rooms(request):
    return render(request, "hotel/rooms.html")


@staff_member_required
@require_GET
def guests(request):
    return render(request, "hotel/guests.html")


@staff_member_required
@require_GET
def check_in(request):
    return render(request, "hotel/check_in.html")
