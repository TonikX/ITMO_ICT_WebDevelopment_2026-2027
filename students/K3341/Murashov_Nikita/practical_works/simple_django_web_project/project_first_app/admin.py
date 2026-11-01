from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership

_extra = ("Данные автовладельца", {"fields": ("birth_date", "passport_number", "home_address", "nationality")})


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (_extra,)
    add_fieldsets = UserAdmin.add_fieldsets + (_extra,)
    list_display = ("username", "last_name", "first_name", "passport_number", "nationality")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("state_number", "brand", "model", "color")
    search_fields = ("state_number", "brand", "model")


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ("owner", "car", "start_date", "end_date")
    list_filter = ("owner", "car")


admin.site.register(DriverLicense)
