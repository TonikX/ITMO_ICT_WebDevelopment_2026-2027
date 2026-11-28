from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, DriverLicense, Owner, Ownership


class OwnershipInline(admin.TabularInline):
    model = Ownership
    extra = 1


class DriverLicenseInline(admin.TabularInline):
    model = DriverLicense
    extra = 0


OWNER_FIELDS = ("birth_date", "passport_number", "home_address", "nationality")


@admin.register(Owner)
class OwnerAdmin(UserAdmin):
    """Практика 2.3: новые поля пользователя отображаются в Django Admin."""

    fieldsets = UserAdmin.fieldsets + (("Данные автовладельца", {"fields": OWNER_FIELDS}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Данные автовладельца", {"fields": ("last_name", "first_name") + OWNER_FIELDS}),
    )
    list_display = ("username", "last_name", "first_name", "passport_number", "nationality", "is_staff")
    search_fields = ("username", "last_name", "first_name", "passport_number")
    inlines = [OwnershipInline, DriverLicenseInline]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "brand", "model", "color")
    search_fields = ("plate_number", "brand", "model")
    inlines = [OwnershipInline]


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ("owner", "car", "start_date", "end_date")
    list_filter = ("car",)


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ("license_number", "license_type", "owner", "issue_date")
    list_filter = ("license_type",)
