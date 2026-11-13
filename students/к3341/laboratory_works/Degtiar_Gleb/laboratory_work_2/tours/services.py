from django.db import transaction
from .models import Booking

def confirm_booking(pk):
    """Идемпотентное подтверждение; используется сайтом и Django Admin."""
    with transaction.atomic():
        booking = Booking.objects.select_for_update().get(pk=pk)
        booking.status = Booking.CONFIRMED
        booking.save(update_fields=['status'])
    return booking
