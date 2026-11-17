from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Car, DriverLicense, Ownership, User

admin.site.register(Car)
admin.site.register(DriverLicense)
admin.site.register(Ownership)


@admin.register(User)
class CarOwnerAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "passport_number",
        "nationality",
        "is_staff",
    )
    search_fields = ("username", "first_name", "last_name", "passport_number")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Данные автовладельца",
            {"fields": ("passport_number", "home_address", "nationality", "birth_date")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Данные автовладельца",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "passport_number",
                    "home_address",
                    "nationality",
                )
            },
        ),
    )
