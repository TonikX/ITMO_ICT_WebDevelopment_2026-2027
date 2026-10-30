from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from . import services

from .models import (
    Accommodation, CleaningSchedule, Employee, Floor, Guest, Room, RoomType, Stay,
)


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = "__all__"

    def validate(self, attrs):
        if self.instance and "capacity" in attrs:
            if attrs["capacity"] != self.instance.capacity and self.instance.rooms.exists():
                raise serializers.ValidationError({"capacity": "Тип уже используется номерами."})
        return attrs


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

    def validate(self, attrs):
        if self.instance and self.instance.accommodations.exists():
            for field in ("floor", "room_type"):
                if field in attrs and attrs[field] != getattr(self.instance, field):
                    raise serializers.ValidationError({field: "Нельзя менять у номера с историей заселений."})
        return attrs


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = "__all__"


class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = ("id", "room", "check_in", "planned_check_out", "actual_check_out", "price_per_night")
        read_only_fields = fields


class StaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Stay
        fields = ("id", "guest", "accommodation")
        read_only_fields = fields


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
        # Назначения меняются только через будущие операции расписания.
        read_only_fields = ("floors",)

    def validate(self, attrs):
        hired = attrs.get("hired_on", getattr(self.instance, "hired_on", None))
        dismissed = attrs.get("dismissed_on", getattr(self.instance, "dismissed_on", None))
        if hired and dismissed and dismissed < hired:
            raise serializers.ValidationError({"dismissed_on": "Увольнение не может быть раньше приёма."})
        if dismissed and dismissed > timezone.localdate():
            raise serializers.ValidationError({"dismissed_on": "Дата увольнения не может быть в будущем."})
        if self.instance:
            if self.instance.dismissed_on and dismissed != self.instance.dismissed_on:
                raise serializers.ValidationError({"dismissed_on": "Нельзя отменять или менять состоявшееся увольнение."})
            if hired != self.instance.hired_on:
                if self.instance.cleaning_assignments.filter(valid_from__lt=hired).exists():
                    raise serializers.ValidationError({"hired_on": "Есть назначения до новой даты приёма."})
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        dismissed = validated_data.pop("dismissed_on", instance.dismissed_on)
        instance = super().update(instance, validated_data)
        if dismissed and instance.dismissed_on is None:
            instance = services.dismiss_employee(instance.pk, dismissed)
        return instance


class CleaningScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningSchedule
        fields = ("id", "employee", "floor", "weekday", "valid_from", "valid_to")
        read_only_fields = fields


class RoomAccommodationsSerializer(RoomSerializer):
    accommodations = AccommodationSerializer(many=True, read_only=True)


class ScheduleEntrySerializer(CleaningScheduleSerializer):
    floor = FloorSerializer(read_only=True)


class EmployeeScheduleSerializer(EmployeeSerializer):
    schedule = ScheduleEntrySerializer(
        source="cleaning_assignments", many=True, read_only=True
    )


class CheckInSerializer(serializers.Serializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    guests = serializers.PrimaryKeyRelatedField(
        queryset=Guest.objects.all(), many=True, allow_empty=False
    )
    check_in = serializers.DateField()
    planned_check_out = serializers.DateField()

    def validate_guests(self, guests):
        if len({guest.pk for guest in guests}) != len(guests):
            raise serializers.ValidationError("Гости не должны повторяться.")
        return guests

    def validate(self, attrs):
        if "price_per_night" in self.initial_data:
            raise serializers.ValidationError({"price_per_night": "Тариф определяется сервером."})
        if attrs["planned_check_out"] <= attrs["check_in"]:
            raise serializers.ValidationError({"planned_check_out": "Выезд должен быть позже заселения."})
        return attrs

    def create(self, validated_data):
        return services.check_in(**validated_data)


class CheckOutSerializer(serializers.Serializer):
    actual_check_out = serializers.DateField()


class DismissEmployeeSerializer(serializers.Serializer):
    dismissed_on = serializers.DateField(default=timezone.localdate)

    def validate_dismissed_on(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Дата увольнения не может быть в будущем.")
        return value


class AccommodationGuestsSerializer(AccommodationSerializer):
    guests = serializers.SerializerMethodField()

    class Meta(AccommodationSerializer.Meta):
        fields = AccommodationSerializer.Meta.fields + ("guests",)
        read_only_fields = fields

    def get_guests(self, instance):
        return list(instance.stays.values_list("guest_id", flat=True))


class CleaningScheduleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningSchedule
        fields = ("id", "employee", "floor", "weekday", "valid_from", "valid_to")
        # Пересечение периодов ниже также исключает точные дубликаты.
        validators = []

    def validate(self, attrs):
        instance = self.instance
        employee = attrs.get("employee", getattr(instance, "employee", None))
        floor = attrs.get("floor", getattr(instance, "floor", None))
        weekday = attrs.get("weekday", getattr(instance, "weekday", None))
        start = attrs.get("valid_from", getattr(instance, "valid_from", None))
        end = attrs.get("valid_to", getattr(instance, "valid_to", None))
        today = timezone.localdate()
        if employee.dismissed_on is not None:
            raise serializers.ValidationError({"employee": "Уволенному сотруднику нельзя назначать уборку."})
        if instance and instance.valid_to and instance.valid_to <= today:
            raise serializers.ValidationError("Историческое назначение нельзя изменять.")
        if instance and instance.valid_from < today:
            start = attrs.get("valid_from", today)
            if start < today:
                raise serializers.ValidationError({"valid_from": "Новую версию нельзя начинать в прошлом."})
        if start < employee.hired_on:
            raise serializers.ValidationError({"valid_from": "Назначение раньше приёма сотрудника."})
        if end is not None and end <= start:
            raise serializers.ValidationError({"valid_to": "Окончание должно быть позже начала."})
        duplicates = CleaningSchedule.objects.filter(
            employee=employee, floor=floor, weekday=weekday
        ).filter(Q(valid_to__isnull=True) | Q(valid_to__gt=start))
        if end is not None:
            duplicates = duplicates.filter(valid_from__lt=end)
        if instance:
            duplicates = duplicates.exclude(pk=instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("Такое назначение уже действует в выбранный период.")
        return attrs

    def update(self, instance, validated_data):
        today = timezone.localdate()
        if instance.valid_from < today:
            start = validated_data.get("valid_from", today)
            values = {
                field: validated_data.get(field, getattr(instance, field))
                for field in ("employee", "floor", "weekday", "valid_to")
            }
            instance.valid_to = min(instance.valid_to, start) if instance.valid_to else start
            instance.save(update_fields=["valid_to"])
            return CleaningSchedule.objects.create(valid_from=start, **values)
        return super().update(instance, validated_data)


class DateRangeQuerySerializer(serializers.Serializer):
    date_from = serializers.DateField()
    date_to = serializers.DateField()

    def validate(self, attrs):
        if attrs["date_to"] <= attrs["date_from"]:
            raise serializers.ValidationError({
                "date_to": "Конец периода должен быть позже начала."
            })
        return attrs


class QuarterlyReportQuerySerializer(serializers.Serializer):
    # Следующий год нужен для правой границы четвёртого квартала.
    year = serializers.IntegerField(min_value=1, max_value=9998)
    quarter = serializers.IntegerField(min_value=1, max_value=4)


class RoomGuestsQuerySerializer(DateRangeQuerySerializer):
    room_id = serializers.IntegerField(min_value=1)


class CityQuerySerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100, allow_blank=False)


class GuestQuerySerializer(serializers.Serializer):
    guest_id = serializers.IntegerField(min_value=1)


class GuestCleanerQuerySerializer(GuestQuerySerializer):
    date = serializers.DateField()


class GuestSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ("id", "first_name", "last_name", "middle_name")
        read_only_fields = fields


class EmployeeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "first_name", "last_name", "middle_name")
        read_only_fields = fields


class RoomSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "number")
        read_only_fields = fields
