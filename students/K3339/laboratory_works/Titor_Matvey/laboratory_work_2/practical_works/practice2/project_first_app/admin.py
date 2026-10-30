
from django.contrib import admin

from .models import Car, Owner, Ownership

class OwnershipInline(admin.TabularInline):
    model = Ownership
    extra = 1

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date')
    search_fields = ('last_name', 'first_name')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'color', 'state_number')
    list_filter = ('brand', 'color')
    search_fields = ('brand', 'model', 'state_number')
    inlines = (OwnershipInline,)

@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('owner', 'car', 'start_date', 'end_date')
    list_filter = ('car__brand',)
    search_fields = ('owner__last_name', 'car__state_number')
