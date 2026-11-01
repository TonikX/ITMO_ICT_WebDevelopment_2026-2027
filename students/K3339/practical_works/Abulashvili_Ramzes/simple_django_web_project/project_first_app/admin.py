from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Car, CarOwner, DrivingLicense, Ownership


@admin.register(CarOwner)
class CarOwnerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Данные автовладельца", {"fields": ("birth_date", "passport_number", "home_address", "nationality")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Данные автовладельца", {"fields": ("first_name", "last_name", "birth_date", "passport_number", "home_address", "nationality")}),)
    list_display = ["username", "first_name", "last_name", "nationality", "is_staff"]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ["plate_number", "brand", "model_name", "color"]
    search_fields = ["plate_number", "brand"]


@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ["owner", "car", "start_date", "end_date"]


admin.site.register(DrivingLicense)
admin.site.site_header = "Автовладельцы — практики Django"
