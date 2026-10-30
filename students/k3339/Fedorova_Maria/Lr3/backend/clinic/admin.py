from django.contrib import admin

from .models import (
    Appointment,
    Cabinet,
    Doctor,
    DoctorSchedule,
    Patient,
    Service,
)


class DoctorScheduleInline(admin.TabularInline):
    model = DoctorSchedule
    extra = 0


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "last_name",
        "first_name",
        "specialty",
        "work_start",
        "work_end",
    )
    list_filter = ("specialty", "gender")
    search_fields = ("last_name", "first_name", "specialty")
    inlines = [DoctorScheduleInline]


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ("id", "number", "responsible", "phone", "work_start", "work_end")
    search_fields = ("number", "phone")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialty", "price")
    list_filter = ("specialty",)
    search_fields = ("name",)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "last_name",
        "first_name",
        "card_number",
        "phone",
        "birth_date",
    )
    search_fields = ("last_name", "first_name", "phone", "card_number", "passport")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "visited_at",
        "diagnosis",
        "cost",
        "is_paid",
    )
    list_editable = ("is_paid",)
    list_filter = ("is_paid", "doctor__specialty")
    search_fields = (
        "patient__last_name",
        "doctor__last_name",
        "diagnosis",
    )
