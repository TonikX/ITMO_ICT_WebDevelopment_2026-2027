from django.contrib import admin
from .models import Car, DriverLicense, Ownership


class OwnershipInline(admin.TabularInline):
    model = Ownership
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'brand', 'model', 'color']
    search_fields = ['registration_number', 'brand']
    inlines = [OwnershipInline]


admin.site.register(Ownership)
admin.site.register(DriverLicense)
