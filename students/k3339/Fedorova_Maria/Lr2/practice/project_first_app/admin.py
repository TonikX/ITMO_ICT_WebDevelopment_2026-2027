from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership

@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Owner profile",
            {
                "fields": (
                    "birth_date",
                    "passport_number",
                    "home_address",
                    "nationality",
                ),
            },
        ),
    )
    list_display = (
        "username",
        "first_name",
        "last_name",
        "passport_number",
        "nationality",
        "is_staff",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "passport_number",
    )

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "model", "color", "state_number")
    search_fields = ("brand", "model", "state_number")

@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "car", "start_date", "end_date")
    list_filter = ("start_date",)

@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "license_number",
        "license_type",
        "issue_date",
    )
    list_filter = ("license_type",)
