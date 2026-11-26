from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .models import Flight, FlightType, Passenger, Passport, Ticket, User
from .services import FlightFullError, create_reservation


class FlightConstraintTests(TestCase):
    def test_database_rejects_arrival_before_departure(self):
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Flight.objects.create(
                    flight_number="BAD-TIME",
                    airline="Test Airline",
                    departure=now,
                    arrival=now - timedelta(minutes=1),
                    flight_type=FlightType.DEPARTURE,
                    gate="A1",
                )


class ReservationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="test-password",
        )
        now = timezone.now()
        self.flight = Flight.objects.create(
            flight_number="TEST-1",
            airline="Test Airline",
            departure=now,
            arrival=now + timedelta(hours=2),
            flight_type=FlightType.DEPARTURE,
            gate="A1",
            capacity=1,
        )
        self.passengers = []
        for first_name in ("First", "Second"):
            passenger = Passenger.objects.create(
                owner=self.user,
                first_name=first_name,
                last_name="Passenger",
                birth_date=timezone.localdate() - timedelta(days=365 * 30),
            )
            Passport.objects.create(
                passenger=passenger,
                passport_number=f"PASSPORT-{first_name}",
            )
            self.passengers.append(passenger)

    def test_reservation_assigns_seat_and_rejects_booking_when_full(self):
        reservation = create_reservation(
            purchaser=self.user,
            flight_id=self.flight.pk,
            passenger_ids=[self.passengers[0].pk],
        )

        ticket = Ticket.objects.get(reservation=reservation)
        self.assertEqual(ticket.seat_number, 1)

        with self.assertRaises(FlightFullError):
            create_reservation(
                purchaser=self.user,
                flight_id=self.flight.pk,
                passenger_ids=[self.passengers[1].pk],
            )

        self.assertEqual(Ticket.objects.filter(flight=self.flight).count(), 1)
        self.assertEqual(self.flight.reservations.count(), 1)
