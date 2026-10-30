from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DriverLicense, Ownership

class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Данные владельца", {
            "fields": ("birth_date", "passport_number", "home_address", "nationality"),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Данные владельца", {
            "fields": (
                "first_name", "last_name", "email", "birth_date",
                "passport_number", "home_address", "nationality",
            ),
        }),
    )
    list_display = (
        "username", "first_name", "last_name", "passport_number",
        "home_address", "nationality", "is_staff",
    )


admin.site.register(CarOwner, CarOwnerAdmin)
admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
