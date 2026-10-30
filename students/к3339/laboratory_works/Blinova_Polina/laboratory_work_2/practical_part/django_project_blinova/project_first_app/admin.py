from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import DriverLicense, Car, Ownership

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'username', 'last_name', 'first_name',
        'email', 'passport_number', 'nationality', 'is_staff'
    )
    list_display_links = ('id', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'nationality')
    search_fields = ('username', 'email', 'last_name', 'first_name', 'passport_number')
    ordering = ('last_name', 'first_name')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('passport_number', 'home_address', 'nationality', 'birth_date')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('passport_number', 'home_address', 'nationality', 'birth_date')
        }),
    )


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'license_number', 'category', 'owner', 'issued_date')
    list_filter = ('category',)
    search_fields = ('license_number', 'owner__last_name', 'owner__first_name')


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand', 'model', 'state_number', 'color')
    list_filter = ('brand', 'color')
    search_fields = ('brand', 'model', 'state_number')


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'car', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('owner__last_name', 'car__state_number')
    date_hierarchy = 'start_date'