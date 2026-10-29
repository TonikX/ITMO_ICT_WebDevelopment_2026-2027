from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Car, CarOwner, DriverLicense, Ownership


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Автовладелец', {'fields': ['birth_date', 'passport_number', 'home_address', 'nationality']}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Автовладелец', {'fields': ['first_name', 'last_name', 'birth_date', 'passport_number', 'home_address', 'nationality']}),)
    list_display = ['username', 'first_name', 'last_name', 'nationality', 'is_staff']


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['plate', 'brand', 'model', 'color']


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ['owner', 'car', 'start_date', 'end_date']


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ['owner', 'number', 'category', 'issue_date']
