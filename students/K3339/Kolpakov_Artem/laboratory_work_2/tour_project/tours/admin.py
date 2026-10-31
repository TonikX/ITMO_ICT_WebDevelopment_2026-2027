from django.contrib import admin

from .models import Country, Reservation, Review, Tour, TravelAgency


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("user", "tour", "is_confirmed")
    list_editable = ("is_confirmed",)


admin.site.register(Country)
admin.site.register(TravelAgency)
admin.site.register(Tour)
admin.site.register(Review)
