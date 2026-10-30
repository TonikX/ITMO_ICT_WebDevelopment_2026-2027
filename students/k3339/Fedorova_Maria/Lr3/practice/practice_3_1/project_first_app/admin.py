from django.contrib import admin

from .models import Car, CarOwner, DriverLicense, Ownership


@admin.register(CarOwner)
class CarOwnerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "birth_date")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "model", "color", "state_number")


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "car", "start_date", "end_date")


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "license_number", "license_type", "issue_date")
