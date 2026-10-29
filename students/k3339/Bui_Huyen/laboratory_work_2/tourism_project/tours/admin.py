from django.contrib import admin, messages
from django.db import transaction
from .models import Country, TourCompany, Tour, Booking, Review, TourImage

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(TourCompany)
class TourCompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone")
    search_fields = ("name", "email")


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    inlines = [TourImageInline]
    list_display = (
        "title",
        "country",
        "company",
        "start_date",
        "end_date",
        "price",
        "available_places",
        "is_active",
    )
    list_filter = ("country", "company", "is_active")
    search_fields = ("title", "description")

@admin.action(description="Подтвердить выбранные бронирования")
def confirm_bookings(modeladmin, request, queryset):
    updated = queryset.filter(
        status=Booking.Status.PENDING
    ).update(
        status=Booking.Status.CONFIRMED
    )

    modeladmin.message_user(
        request,
        f"Подтверждено бронирований: {updated}",
        level=messages.SUCCESS,
    )

confirm_bookings.short_description = (
    "Подтвердить выбранные бронирования"
)



@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tour",
        "people_count",
        "booking_date",
        "status",
    )
    list_filter = ("status", "booking_date")
    search_fields = ("user__username", "tour__title")
    actions = [confirm_bookings]

    def _restore_places(self, queryset):
        # Получаем актуальные бронирования и блокируем их на время обработки.
        bookings = list(
            Booking.objects.select_for_update()
            .filter(pk__in=queryset.values("pk"))
            .order_by("pk")
        )

        # Отмененные бронирования уже вернули места при отмене пользователем.
        places_by_tour = {}

        for booking in bookings:
            if booking.status != Booking.Status.CANCELLED:
                places_by_tour[booking.tour_id] = (
                    places_by_tour.get(booking.tour_id, 0)
                    + booking.people_count
                )

        if not places_by_tour:
            return

        # Блокируем туры и возвращаем места
        tours = list(
            Tour.objects.select_for_update()
            .filter(pk__in=places_by_tour.keys())
            .order_by("pk")
        )

        for tour in tours:
            tour.available_places += places_by_tour[tour.pk]

        Tour.objects.bulk_update(
            tours,
            ["available_places"],
        )

    def delete_model(self, request, obj):
        # Удаление одной записи
        with transaction.atomic():
            self._restore_places(
                Booking.objects.filter(pk=obj.pk)
            )
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # Удаление нескольких записей через действие Delete selected bookings.
        with transaction.atomic():
            self._restore_places(queryset)
            super().delete_queryset(request, queryset)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "tour",
        "score",
        "review_date",
    )
    list_filter = ("score", "review_date")
    search_fields = (
        "user__username",
        "tour__title",
        "content",
    )