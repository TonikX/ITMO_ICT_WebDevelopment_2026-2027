from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership

OWNER_FIELDS = ('birth_date', 'passport', 'address', 'nationality')


class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Данные автовладельца', {'fields': OWNER_FIELDS}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Данные автовладельца', {'fields': ('last_name', 'first_name') + OWNER_FIELDS}),
    )
    list_display = ['username', 'last_name', 'first_name', 'passport', 'nationality', 'is_staff']


class CarAdmin(admin.ModelAdmin):
    list_display = ['plate', 'brand', 'model_name', 'color']


class OwnershipAdmin(admin.ModelAdmin):
    list_display = ['owner', 'car', 'start_date', 'end_date']
    list_filter = ['owner']


class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ['number', 'owner', 'kind', 'issue_date']


admin.site.register(CarOwner, CarOwnerAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Ownership, OwnershipAdmin)
admin.site.register(DriverLicense, DriverLicenseAdmin)
