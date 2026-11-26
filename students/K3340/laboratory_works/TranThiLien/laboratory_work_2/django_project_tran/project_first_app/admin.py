from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership


class OwnershipInline(admin.TabularInline):
    model = Ownership
    extra = 1


class DriverLicenseInline(admin.TabularInline):
    model = DriverLicense
    extra = 0


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    """Практика 2.3: новые поля пользователя видны в Django Admin."""
    list_display = ('username', 'last_name', 'first_name', 'passport_number',
                    'nationality', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Данные автовладельца', {
            'fields': ('birth_date', 'passport_number', 'home_address', 'nationality'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные автовладельца', {
            'fields': ('first_name', 'last_name', 'birth_date',
                       'passport_number', 'home_address', 'nationality'),
        }),
    )
    inlines = [DriverLicenseInline, OwnershipInline]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'brand', 'model', 'color')
    inlines = [OwnershipInline]


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('owner', 'car', 'start_date', 'end_date')


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ('number', 'owner', 'type', 'issue_date')
