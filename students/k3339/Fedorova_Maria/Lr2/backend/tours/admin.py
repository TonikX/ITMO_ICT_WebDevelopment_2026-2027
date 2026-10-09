from django.contrib import admin

from .models import Agency, Country, Reservation, Review, Tour

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "country",
        "agency",
        "start_date",
        "end_date",
        "price",
    )
    list_filter = ("country", "agency")
    search_fields = ("name", "description")

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tour",
        "start_date",
        "end_date",
        "created_at",
        "is_confirmed",
    )
    list_editable = ("is_confirmed",)
    list_filter = ("is_confirmed",)
    search_fields = ("user__username", "tour__name")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tour",
        "rating",
        "start_date",
        "end_date",
        "created_at",
    )
    list_filter = ("rating",)
    search_fields = ("user__username", "tour__name", "text")
