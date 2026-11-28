from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q, F, Sum

from .models import Aircraft, Route, Flight, Employee, AircraftType


class AircraftMostFrequentRouteView(APIView):
    def get(self, request):
        rows = (
            Flight.objects
            .values("aircraft__aircraft_type__model", "route")
            .annotate(flights_count=Count("id"))
            .order_by("-flights_count")
        )
        result = {}
        for r in rows:
            model = r["aircraft__aircraft_type__model"]
            if model not in result or r["flights_count"] > result[model]["flights_count"]:
                result[model] = {
                    "route_id": r["route"],
                    "flights_count": r["flights_count"],
                }
        return Response(result)


class UnderfilledRoutesView(APIView):
    def get(self, request):
        percent = int(request.query_params.get("percent", 50))
        rows = (
            Flight.objects
            .filter(tickets_sold__lt=F("aircraft__seats") * percent / 100)
            .values("route")
            .annotate(count=Count("id"))
            .order_by("route")
        )
        return Response({
            "percent_threshold": percent,
            "routes": list(rows),
        })


class FlightFreeSeatsView(APIView):
    def get(self, request, pk):
        try:
            flight = Flight.objects.select_related("aircraft").get(pk=pk)
        except Flight.DoesNotExist:
            return Response({"detail": "Flight not found"}, status=404)
        free = flight.aircraft.seats - flight.tickets_sold
        return Response({
            "flight_id": flight.id,
            "flight_number": flight.flight_number,
            "seats_total": flight.aircraft.seats,
            "tickets_sold": flight.tickets_sold,
            "free_seats": free,
        })


class AircraftInRepairView(APIView):
    def get(self, request):
        count = Aircraft.objects.filter(status="repair").count()
        return Response({"aircraft_in_repair": count})


class CompanyEmployeesCountView(APIView):
    def get(self, request):
        rows = (
            Employee.objects
            .values("company__name")
            .annotate(count=Count("id"))
            .order_by("company__name")
        )
        return Response(list(rows))


class CompanyAircraftsReportView(APIView):
    def get(self, request):
        total = Aircraft.objects.count()
        by_type = (
            Aircraft.objects
            .values("aircraft_type__model", "aircraft_type__manufacturer")
            .annotate(count=Count("id"))
            .order_by("aircraft_type__model")
        )
        return Response({
            "total_aircrafts": total,
            "by_type": list(by_type),
        })