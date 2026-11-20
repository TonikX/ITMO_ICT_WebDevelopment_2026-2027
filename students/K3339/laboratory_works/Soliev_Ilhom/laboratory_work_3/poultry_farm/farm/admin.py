from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Breed,
    BreedSeasonDiet,
    Cage,
    Chicken,
    ChickenCageAssignment,
    ChickenWeightRecord,
    Diet,
    EggProductionRecord,
    Employee,
    EmployeeCageAssignment,
    EmploymentContract,
    FarmUser,
    Workshop,
)


@admin.register(FarmUser)
class FarmUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Птицефабрика", {"fields": ("role", "created_at")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Птицефабрика", {"fields": ("role",)}),)
    readonly_fields = ("created_at",)
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "passport_series", "passport_number")
    search_fields = ("full_name", "passport_series", "passport_number")
    list_select_related = ("user",)


@admin.register(EmploymentContract)
class EmploymentContractAdmin(admin.ModelAdmin):
    list_display = ("contract_number", "employee", "started_at", "ended_at", "salary")
    list_filter = ("started_at", "ended_at")
    search_fields = ("contract_number", "employee__full_name")
    list_select_related = ("employee",)


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("workshop_number", "name", "capacity_cages")
    search_fields = ("name",)


@admin.register(Cage)
class CageAdmin(admin.ModelAdmin):
    list_display = ("workshop", "row_number", "cage_number", "capacity_chickens")
    list_filter = ("workshop",)
    list_select_related = ("workshop",)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("name", "average_eggs_per_month", "average_weight_grams")
    search_fields = ("name",)


@admin.register(Chicken)
class ChickenAdmin(admin.ModelAdmin):
    list_display = ("id", "breed", "birth_date", "arrived_at", "removed_at", "removal_reason")
    list_filter = ("breed", "removal_reason")
    list_select_related = ("breed",)


@admin.register(ChickenWeightRecord)
class ChickenWeightRecordAdmin(admin.ModelAdmin):
    list_display = ("chicken", "measured_at", "weight_grams")
    list_filter = ("measured_at",)
    list_select_related = ("chicken",)


@admin.register(ChickenCageAssignment)
class ChickenCageAssignmentAdmin(admin.ModelAdmin):
    list_display = ("chicken", "cage", "valid_from", "valid_to")
    list_filter = ("cage__workshop", "valid_to")
    list_select_related = ("chicken", "cage__workshop")


@admin.register(EmployeeCageAssignment)
class EmployeeCageAssignmentAdmin(admin.ModelAdmin):
    list_display = ("employee", "cage", "assigned_from", "assigned_to")
    list_filter = ("cage__workshop", "assigned_to")
    list_select_related = ("employee", "cage__workshop")


@admin.register(EggProductionRecord)
class EggProductionRecordAdmin(admin.ModelAdmin):
    list_display = ("chicken", "production_date", "eggs_count")
    list_filter = ("production_date",)
    list_select_related = ("chicken",)


@admin.register(Diet)
class DietAdmin(admin.ModelAdmin):
    list_display = ("diet_number", "daily_cost_per_chicken")
    search_fields = ("diet_number", "content")


@admin.register(BreedSeasonDiet)
class BreedSeasonDietAdmin(admin.ModelAdmin):
    list_display = ("breed", "season", "diet")
    list_filter = ("season",)
    list_select_related = ("breed", "diet")
