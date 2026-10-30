from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Appointment, Doctor, DoctorSchedule, Patient, Service


class ClinicApiTests(TestCase):
    """
    ClinicApiTests

    Role-based access for admin / doctor / patient.
    """

    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            username="staff",
            password="secret12",
            is_staff=True,
        )
        self.doctor_user = User.objects.create_user(
            username="doc",
            password="secret12",
        )
        self.patient_user = User.objects.create_user(
            username="pat",
            password="secret12",
        )
        self.stranger = User.objects.create_user(
            username="stranger",
            password="secret12",
        )
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            last_name="Смирнова",
            first_name="Анна",
            specialty="Отоларинголог",
            education="СПбГМУ",
            gender=Doctor.Gender.FEMALE,
            birth_date=date(1985, 1, 1),
            work_start=date(2015, 1, 1),
            contract_number="D-1",
            contract_date=date(2015, 1, 1),
        )
        DoctorSchedule.objects.create(
            doctor=self.doctor,
            weekday=0,
            is_working=True,
        )
        self.service = Service.objects.create(
            name="Приём ЛОР",
            specialty="Отоларинголог",
            price=Decimal("2500.00"),
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            last_name="Орлова",
            first_name="Елена",
            birth_date=date(1990, 5, 5),
            gender=Patient.Gender.FEMALE,
            phone="+79001112233",
            address="SPB",
            passport="4010 111111",
            card_number="MC-10",
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            service=self.service,
            visited_at=timezone.now(),
            diagnosis="Отит",
            condition="OK",
            cost=self.service.price,
            is_paid=False,
        )

    def _auth(self, user):
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_djoser_register_and_me_roles(self):
        response = self.client.post(
            "/api/auth/users/",
            {
                "username": "newbie",
                "password": "ClinicPass123",
                "email": "n@example.com",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        login = self.client.post(
            "/api/auth/token/login/",
            {"username": "newbie", "password": "ClinicPass123"},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {login.data['auth_token']}",
        )
        me = self.client.get("/api/auth/users/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["role"], "guest")
        self.assertFalse(me.data["is_patient"])

    def test_stranger_cannot_see_patients(self):
        self._auth(self.stranger)
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patient_sees_own_appointments_and_pays(self):
        self._auth(self.patient_user)
        appointments = self.client.get("/api/appointments/")
        self.assertEqual(appointments.status_code, status.HTTP_200_OK)
        self.assertEqual(appointments.data["count"], 1)

        pay = self.client.patch(f"/api/appointments/{self.appointment.id}/pay/")
        self.assertEqual(pay.status_code, status.HTTP_200_OK)
        self.assertTrue(pay.data["is_paid"])

        book = self.client.post(
            "/api/appointments/",
            {
                "doctor": self.doctor.id,
                "service": self.service.id,
                "visited_at": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(book.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.data["patient"], self.patient.id)
        self.assertEqual(book.data["diagnosis"], "")

    def test_doctor_creates_appointment_for_self(self):
        self._auth(self.doctor_user)
        response = self.client.post(
            "/api/appointments/",
            {
                "patient": self.patient.id,
                "doctor": 999,
                "service": self.service.id,
                "visited_at": timezone.now().isoformat(),
                "diagnosis": "Ринит",
                "condition": "Лёгкое",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["doctor"], self.doctor.id)

        patients = self.client.get("/api/patients/")
        self.assertEqual(patients.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(patients.data["count"], 1)

        mine = self.client.get("/api/analytics/doctor-patients/")
        self.assertEqual(mine.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(mine.data), 1)

    def test_staff_analytics(self):
        self._auth(self.staff)
        ent = self.client.get("/api/analytics/ent-patients/")
        self.assertEqual(ent.status_code, status.HTTP_200_OK)
        self.assertEqual(len(ent.data), 1)

        self._auth(self.doctor_user)
        forbidden = self.client.get("/api/analytics/ent-patients/")
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
