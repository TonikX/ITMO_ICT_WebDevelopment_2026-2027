from django.contrib import admin
from .models import Car, DriverLicense, Ownership


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'brand', 'model_name', 'color')
    search_fields = ('plate_number', 'brand')


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('owner', 'car', 'start_date', 'end_date')


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ('owner', 'number', 'category', 'issued_at')
