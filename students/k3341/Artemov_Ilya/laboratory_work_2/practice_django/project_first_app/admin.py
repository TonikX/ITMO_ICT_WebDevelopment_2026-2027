from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import OwnerCreationForm
from .models import Car, CarOwner, DriverLicense, Ownership


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    add_form = OwnerCreationForm
    fieldsets = UserAdmin.fieldsets + (("Данные автовладельца", {"fields": (
        "birth_date", "passport_number", "home_address", "nationality",
    )}),)
    add_fieldsets = ((None, {"fields": (
        "username", "password1", "password2", "first_name", "last_name", "email",
        "birth_date", "passport_number", "home_address", "nationality",
    )}),)
    list_display = ["username", "first_name", "last_name", "passport_number", "nationality"]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "brand", "model_name", "color"]
    search_fields = ["registration_number", "brand", "model_name"]


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ["owner", "car", "start_date", "end_date"]
    list_select_related = ["owner", "car"]


@admin.register(DriverLicense)
class DriverLicenseAdmin(admin.ModelAdmin):
    list_display = ["number", "owner", "category", "issue_date"]
