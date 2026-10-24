from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DrivingLicense, Ownership


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Данные владельца', {
            'fields': ('birth_date', 'passport_number', 'address', 'nationality'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные владельца', {
            'fields': (
                'first_name',
                'last_name',
                'birth_date',
                'passport_number',
                'address',
                'nationality',
            ),
        }),
    )
    list_display = (
        'username',
        'last_name',
        'first_name',
        'passport_number',
        'address',
        'nationality',
    )
    search_fields = ('username', 'last_name', 'first_name', 'passport_number')


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'brand', 'model_name', 'color')
    search_fields = ('license_plate', 'brand', 'model_name')


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('owner', 'car', 'start_date', 'end_date')
    list_filter = ('start_date',)


@admin.register(DrivingLicense)
class DrivingLicenseAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'license_type', 'owner', 'issue_date')
    list_filter = ('license_type',)
