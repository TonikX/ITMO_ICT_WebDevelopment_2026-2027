from django.contrib import admin
from django.db import transaction
from .models import Flight, Reservation, Review


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ["number", "airline", "origin", "destination", "departure_at", "direction", "gate"]
    list_filter = ["direction", "airline", "departure_at"]
    search_fields = ["number", "origin", "destination"]

    def get_form(self, request, obj=None, **kwargs):
        base_form = super().get_form(request, obj, **kwargs)

        class LockedFlightForm(base_form):
            def clean(self):
                data = super().clean()
                if self.instance.pk and transaction.get_connection().in_atomic_block:
                    Flight.objects.select_for_update().get(pk=self.instance.pk)
                return data

        return LockedFlightForm


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["flight", "passenger_name", "seat_number", "ticket_number", "checked_in", "user"]
    list_filter = ["checked_in", "flight"]
    search_fields = ["passenger_name", "ticket_number", "user__username", "flight__number"]
    list_select_related = ["flight", "user"]
    readonly_fields = ["created_at"]

    def get_form(self, request, obj=None, **kwargs):
        base_form = super().get_form(request, obj, **kwargs)

        class LockedReservationForm(base_form):
            def clean(self):
                data = super().clean()
                flight = data.get("flight")
                if flight and transaction.get_connection().in_atomic_block:
                    data["flight"] = Flight.objects.select_for_update().get(pk=flight.pk)
                return data

        return LockedReservationForm


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["flight", "user", "flight_date", "rating", "created_at"]
    list_filter = ["rating", "flight_date"]
    search_fields = ["text", "user__username", "flight__number"]
    list_select_related = ["flight", "user"]
