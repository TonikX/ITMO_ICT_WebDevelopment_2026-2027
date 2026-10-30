from django.db import transaction
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from . import services
from .models import (
    Accommodation, CleaningSchedule, Employee, Floor, Guest, Room, RoomType, Stay,
)
from .serializers import (
    AccommodationGuestsSerializer, AccommodationSerializer, CheckInSerializer,
    CheckOutSerializer, CleaningScheduleWriteSerializer,
    DismissEmployeeSerializer, EmployeeScheduleSerializer,
    EmployeeSerializer, FloorSerializer, GuestSerializer, RoomAccommodationsSerializer,
    RoomSerializer, RoomTypeSerializer, StaySerializer,
    CityQuerySerializer, DateRangeQuerySerializer, EmployeeSummarySerializer,
    GuestCleanerQuerySerializer, GuestQuerySerializer, GuestSummarySerializer,
    RoomGuestsQuerySerializer, RoomSummarySerializer, QuarterlyReportQuerySerializer,
)


class ProtectedDetailView(generics.RetrieveUpdateDestroyAPIView):
    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({"detail": "Удаление запрещено: объект используется связанными записями."})


class QuarterlyReportView(APIView):
    def get(self, request):
        params = QuarterlyReportQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        return Response(services.quarterly_report(**params.validated_data))


class RoomTypeListCreateView(generics.ListCreateAPIView):
    queryset = RoomType.objects.order_by("id")
    serializer_class = RoomTypeSerializer


class RoomTypeDetailView(ProtectedDetailView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer


class FloorListCreateView(generics.ListCreateAPIView):
    queryset = Floor.objects.order_by("id")
    serializer_class = FloorSerializer


class FloorDetailView(ProtectedDetailView):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer


class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.order_by("id")
    serializer_class = RoomSerializer


class RoomDetailView(ProtectedDetailView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        get_object_or_404(Room.objects.select_for_update(), pk=kwargs["pk"])
        return super().update(request, *args, **kwargs)


class GuestListCreateView(generics.ListCreateAPIView):
    queryset = Guest.objects.order_by("id")
    serializer_class = GuestSerializer


class GuestDetailView(ProtectedDetailView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.order_by("id")
    serializer_class = EmployeeSerializer


class EmployeeDetailView(ProtectedDetailView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        get_object_or_404(Employee.objects.select_for_update(), pk=kwargs["pk"])
        return super().update(request, *args, **kwargs)


class AccommodationListView(generics.ListAPIView):
    queryset = Accommodation.objects.order_by("id")
    serializer_class = AccommodationSerializer


class AccommodationDetailView(generics.RetrieveAPIView):
    queryset = Accommodation.objects.all()
    serializer_class = AccommodationSerializer


class StayListView(generics.ListAPIView):
    queryset = Stay.objects.order_by("id")
    serializer_class = StaySerializer


class StayDetailView(generics.RetrieveAPIView):
    queryset = Stay.objects.all()
    serializer_class = StaySerializer


class CleaningScheduleListView(generics.ListCreateAPIView):
    queryset = CleaningSchedule.objects.order_by("id")
    serializer_class = CleaningScheduleWriteSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        employee = get_object_or_404(
            Employee.objects.select_for_update(),
            pk=serializer.validated_data["employee"].pk,
        )
        serializer.validated_data["employee"] = employee
        # Повторная проверка после блокировки защищает от увольнения и дублей.
        serializer.validate(serializer.validated_data)
        serializer.save()


class CleaningScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CleaningSchedule.objects.all()
    serializer_class = CleaningScheduleWriteSerializer
    http_method_names = ["get", "patch", "delete", "head", "options"]

    @transaction.atomic
    def perform_update(self, serializer):
        old_employee_id = serializer.instance.employee_id
        new_employee = serializer.validated_data.get("employee")
        employee_ids = {old_employee_id}
        if new_employee:
            employee_ids.add(new_employee.pk)
        employees = {
            employee.pk: employee for employee in
            Employee.objects.select_for_update().filter(
                pk__in=employee_ids
            ).order_by("pk")
        }
        instance = get_object_or_404(
            CleaningSchedule.objects.select_for_update(), pk=serializer.instance.pk
        )
        if instance.employee_id != old_employee_id:
            raise ValidationError("Назначение изменилось. Повторите запрос.")
        serializer.instance = instance
        if new_employee:
            if new_employee.pk not in employees:
                raise ValidationError({"employee": "Сотрудник больше не существует."})
            serializer.validated_data["employee"] = employees[new_employee.pk]
        serializer.validate(serializer.validated_data)
        serializer.save()

    @transaction.atomic
    def perform_destroy(self, instance):
        get_object_or_404(Employee.objects.select_for_update(), pk=instance.employee_id)
        current = get_object_or_404(
            CleaningSchedule.objects.select_for_update(), pk=instance.pk
        )
        if current.employee_id != instance.employee_id:
            raise ValidationError("Назначение изменилось. Повторите запрос.")
        today = timezone.localdate()
        if current.valid_to and current.valid_to <= today:
            raise ValidationError("Завершённое назначение сохраняется в истории.")
        if current.valid_from >= today:
            current.delete()
        else:
            current.valid_to = today
            current.save(update_fields=["valid_to"])


class RoomAccommodationsView(generics.RetrieveAPIView):
    queryset = Room.objects.prefetch_related("accommodations")
    serializer_class = RoomAccommodationsSerializer


class EmployeeScheduleView(generics.RetrieveAPIView):
    queryset = Employee.objects.prefetch_related(
        "floors",
        Prefetch("cleaning_assignments", queryset=CleaningSchedule.objects.select_related("floor")),
    )
    serializer_class = EmployeeScheduleSerializer


class CheckInView(generics.GenericAPIView):
    serializer_class = CheckInSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        accommodation = serializer.save()
        return Response(
            AccommodationGuestsSerializer(accommodation).data,
            status=status.HTTP_201_CREATED,
        )


class CheckOutView(generics.GenericAPIView):
    serializer_class = CheckOutSerializer

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        accommodation = services.check_out(pk, **serializer.validated_data)
        return Response(AccommodationGuestsSerializer(accommodation).data)


class DismissEmployeeView(generics.GenericAPIView):
    serializer_class = DismissEmployeeSerializer

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = services.dismiss_employee(pk, **serializer.validated_data)
        return Response(EmployeeSerializer(employee).data)


class RoomGuestsAnalyticsView(APIView):
    def get(self, request):
        params = RoomGuestsQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        data = params.validated_data
        room = get_object_or_404(Room, pk=data["room_id"])
        accommodations = services.overlapping_accommodations(
            data["date_from"], data["date_to"]
        ).filter(room=room)
        guests = Guest.objects.filter(
            stays__accommodation__in=accommodations
        ).distinct().order_by("pk")
        result = GuestSummarySerializer(guests, many=True).data
        return Response({
            "room_id": room.pk,
            "date_from": data["date_from"].isoformat(),
            "date_to": data["date_to"].isoformat(),
            "guests": result,
            "count": len(result),
        })


class GuestsByCityAnalyticsView(APIView):
    def get(self, request):
        params = CityQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        city = params.validated_data["city"]
        return Response({
            "city": city,
            "count": Guest.objects.filter(arrival_city__iexact=city).count(),
        })


class GuestCleanerAnalyticsView(APIView):
    def get(self, request):
        params = GuestCleanerQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        guest = get_object_or_404(Guest, pk=params.validated_data["guest_id"])
        day = params.validated_data["date"]
        accommodation = Accommodation.objects.filter(
            stays__guest=guest, check_in__lte=day
        ).filter(
            Q(actual_check_out__gt=day)
            | Q(actual_check_out__isnull=True, planned_check_out__gt=day)
        ).select_related("room").order_by("pk").first()
        response = {
            "guest_id": guest.pk, "date": day.isoformat(),
            "room_id": None, "floor_id": None, "employees": [],
        }
        if accommodation is None:
            response["message"] = "Гость не проживал в гостинице в указанную дату."
            return Response(response)
        room = accommodation.room
        assignments = CleaningSchedule.objects.filter(
            floor_id=room.floor_id, weekday=day.weekday(), valid_from__lte=day,
            employee__hired_on__lte=day,
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gt=day)
        ).filter(
            Q(employee__dismissed_on__isnull=True)
            | Q(employee__dismissed_on__gt=day)
        )
        employees = Employee.objects.filter(
            pk__in=assignments.values("employee_id")
        ).distinct().order_by("pk")
        response.update({
            "room_id": room.pk, "floor_id": room.floor_id,
            "employees": EmployeeSummarySerializer(employees, many=True).data,
        })
        return Response(response)


class AvailableRoomsAnalyticsView(APIView):
    def get(self, request):
        params = DateRangeQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        data = params.validated_data
        occupied = services.overlapping_accommodations(
            data["date_from"], data["date_to"]
        )
        rooms = Room.objects.exclude(
            pk__in=occupied.values("room_id")
        ).order_by("pk")
        result = RoomSummarySerializer(rooms, many=True).data
        return Response({
            "date_from": data["date_from"].isoformat(),
            "date_to": data["date_to"].isoformat(),
            "rooms": result, "count": len(result),
        })


class ConcurrentGuestsAnalyticsView(APIView):
    def get(self, request):
        params = GuestQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        guest = get_object_or_404(Guest, pk=params.validated_data["guest_id"])
        accommodations = Accommodation.objects.filter(stays__guest=guest)
        conditions = Q(pk__in=[])
        # Объединяем пересечения со всеми заездами выбранного гостя.
        for accommodation in accommodations:
            end = accommodation.actual_check_out or accommodation.planned_check_out
            overlaps = services.overlapping_accommodations(
                accommodation.check_in, end
            )
            conditions |= Q(stays__accommodation__in=overlaps)
        guests = Guest.objects.filter(conditions).exclude(
            pk=guest.pk
        ).distinct().order_by("pk")
        result = GuestSummarySerializer(guests, many=True).data
        return Response({
            "guest_id": guest.pk, "guests": result, "count": len(result),
        })
