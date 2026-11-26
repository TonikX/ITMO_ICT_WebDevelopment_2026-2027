from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Flight, Passenger, Passport, Reservation, Review, Ticket, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройка отображения кастомной модели пользователя."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_staff",
    )
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Дополнительная информация", {"fields": ("phone_number",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Дополнительная информация", {"fields": ("email", "phone_number")}),
    )


class PassportInline(admin.TabularInline):
    """Вложенное редактирование паспортов прямо внутри карточки пассажира."""

    model = Passport
    extra = 1


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    """Управление пассажирами."""

    list_display = ("last_name", "first_name", "birth_date", "owner")
    list_select_related = ("owner",)
    search_fields = ("last_name", "first_name", "owner__username", "owner__email")
    list_filter = ("birth_date",)
    inlines = [PassportInline]


@admin.register(Passport)
class PassportAdmin(admin.ModelAdmin):
    """Управление паспортами пассажиров."""

    list_display = ("passport_number", "passenger", "is_active")
    list_select_related = ("passenger",)
    list_filter = ("is_active",)
    search_fields = (
        "passport_number",
        "passenger__last_name",
        "passenger__first_name",
    )


class TicketInline(admin.TabularInline):
    """Вложенная таблица билетов внутри бронирования и рейса."""

    model = Ticket
    extra = 0
    fields = ("passenger", "flight", "seat_number", "ticket_number", "is_checked_in")
    readonly_fields = ("passenger", "flight")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """Управление рейсами."""

    list_display = (
        "flight_number",
        "airline",
        "flight_type",
        "departure",
        "arrival",
        "gate",
        "capacity",
    )
    list_filter = ("flight_type", "airline", "departure")
    search_fields = ("flight_number", "airline", "gate")
    ordering = ("-departure",)
    inlines = [TicketInline]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Управление бронированиями."""

    list_display = ("id", "purchaser", "flight", "created_at")
    list_select_related = ("purchaser", "flight")
    list_filter = ("created_at", "flight__airline")
    search_fields = (
        "purchaser__username",
        "purchaser__email",
        "flight__flight_number",
    )
    readonly_fields = ("created_at",)
    inlines = [TicketInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Управление билетами.
    Позволяет администратору регистрировать пассажира на рейс (is_checked_in)
    и вводить номер билета (ticket_number) прямо из общего списка.
    """

    list_display = (
        "id",
        "flight",
        "passenger",
        "seat_number",
        "ticket_number",
        "is_checked_in",
    )
    list_select_related = ("flight", "passenger", "reservation")
    list_editable = ("ticket_number", "is_checked_in")
    list_filter = ("is_checked_in", "flight__flight_type", "flight__airline")
    search_fields = (
        "ticket_number",
        "passenger__last_name",
        "passenger__first_name",
        "flight__flight_number",
    )
    actions = ["check_in_passengers"]

    @admin.action(description="Зарегистрировать выбранных пассажиров на рейс")
    def check_in_passengers(
        self,
        request: HttpRequest,
        queryset: QuerySet[Ticket],
    ) -> None:
        updated_count = queryset.update(is_checked_in=True)
        self.message_user(
            request,
            f"Успешно зарегистрировано пассажиров: {updated_count}.",
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Управление отзывами о рейсах."""

    list_display = ("flight", "author", "rating", "flight_date", "created_at")
    list_select_related = ("flight", "author")
    list_filter = ("rating", "flight_date", "created_at")
    search_fields = ("flight__flight_number", "author__username", "text")
    readonly_fields = ("created_at",)