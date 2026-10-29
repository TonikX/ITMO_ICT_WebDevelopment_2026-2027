from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Данные владельца", {"fields": ("birth_date", "passport_number", "home_address", "nationality")}),
    )


admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
