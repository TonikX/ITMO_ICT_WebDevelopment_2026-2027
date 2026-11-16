from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Owner, Car, Ownership, DrivingLicence


@admin.register(Owner)
class OwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Данные владельца', {'fields': ('birth_date', 'passport_number', 'home_address', 'nationality')}),)


admin.site.register([Car, Ownership, DrivingLicence])
