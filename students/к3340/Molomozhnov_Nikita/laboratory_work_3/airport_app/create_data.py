import os
import django
from datetime import datetime, date
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project_molomozhnov.settings')
django.setup()

from airport_app.models import (
    CompanyType, Company, AircraftType, Aircraft, Airport, Route,
    Crew, Employee, Flight, TransitStop, CrewMember, Admission,
)


def aware(y, m, d, h=0, mi=0):
    return timezone.make_aware(datetime(y, m, d, h, mi))


# CompanyType
ct_airline, _ = CompanyType.objects.get_or_create(name="Авиакомпания")
ct_service, _ = CompanyType.objects.get_or_create(name="Сервисная")

# Company
aeroflot, _ = Company.objects.get_or_create(
    name="Аэрофлот", defaults={"company_type": ct_airline}
)
s7, _ = Company.objects.get_or_create(
    name="S7 Airlines", defaults={"company_type": ct_airline}
)
airport_admin, _ = Company.objects.get_or_create(
    name="Администрация аэропорта", defaults={"company_type": ct_service}
)

# AircraftType
boeing, _ = AircraftType.objects.get_or_create(
    model="737-800", defaults={"manufacturer": "Boeing"}
)
airbus, _ = AircraftType.objects.get_or_create(
    model="A320", defaults={"manufacturer": "Airbus"}
)
ssj, _ = AircraftType.objects.get_or_create(
    model="SSJ-100", defaults={"manufacturer": "Sukhoi"}
)

# Airport
svo, _ = Airport.objects.get_or_create(name="Шереметьево", defaults={"city": "Москва"})
led, _ = Airport.objects.get_or_create(name="Пулково", defaults={"city": "Санкт-Петербург"})
kzn, _ = Airport.objects.get_or_create(name="Казань", defaults={"city": "Казань"})
ekb, _ = Airport.objects.get_or_create(name="Кольцово", defaults={"city": "Екатеринбург"})

# Route
r1, _ = Route.objects.get_or_create(
    departure_airport=svo, destination_airport=led, defaults={"distance": 650}
)
r2, _ = Route.objects.get_or_create(
    departure_airport=svo, destination_airport=kzn, defaults={"distance": 720}
)
r3, _ = Route.objects.get_or_create(
    departure_airport=svo, destination_airport=ekb, defaults={"distance": 1420}
)

# Aircraft
a1, _ = Aircraft.objects.get_or_create(
    register_number="RA-73001",
    defaults={
        "aircraft_type": boeing, "company": aeroflot,
        "seats": 180, "speed": 850, "status": "operational",
    },
)
a2, _ = Aircraft.objects.get_or_create(
    register_number="RA-73002",
    defaults={
        "aircraft_type": airbus, "company": aeroflot,
        "seats": 160, "speed": 830, "status": "repair",
    },
)
a3, _ = Aircraft.objects.get_or_create(
    register_number="RA-89001",
    defaults={
        "aircraft_type": ssj, "company": s7,
        "seats": 100, "speed": 800, "status": "operational",
    },
)

# Crew
crew1, _ = Crew.objects.get_or_create(name="Экипаж A")
crew2, _ = Crew.objects.get_or_create(name="Экипаж B")

# Employee
e1, _ = Employee.objects.get_or_create(
    full_name="Петров Пётр Петрович",
    defaults={
        "birth_date": date(1980, 1, 1), "education": "Высшее лётное",
        "experience_years": 15, "passport_data": "4500 123456",
        "company": aeroflot, "employment_status": "working",
        "hire_date": date(2010, 5, 1),
    },
)
e2, _ = Employee.objects.get_or_create(
    full_name="Сидоров Сидор Сидорович",
    defaults={
        "birth_date": date(1985, 6, 15), "education": "Высшее лётное",
        "experience_years": 10, "passport_data": "4501 654321",
        "company": aeroflot, "employment_status": "working",
        "hire_date": date(2015, 3, 10),
    },
)
e3, _ = Employee.objects.get_or_create(
    full_name="Иванова Анна Ивановна",
    defaults={
        "birth_date": date(1992, 9, 20), "education": "Среднее специальное",
        "experience_years": 5, "passport_data": "4502 111222",
        "company": aeroflot, "employment_status": "working",
        "hire_date": date(2019, 7, 1),
    },
)
e4, _ = Employee.objects.get_or_create(
    full_name="Кузнецов Кузьма Кузьмич",
    defaults={
        "birth_date": date(1975, 4, 5), "education": "Высшее техническое",
        "experience_years": 20, "passport_data": "4503 333444",
        "company": airport_admin, "employment_status": "working",
        "hire_date": date(2005, 2, 1),
    },
)

# CrewMember
CrewMember.objects.get_or_create(crew=crew1, employee=e1, defaults={"role": "Командир"})
CrewMember.objects.get_or_create(crew=crew1, employee=e2, defaults={"role": "Второй пилот"})
CrewMember.objects.get_or_create(crew=crew1, employee=e3, defaults={"role": "Стюардесса"})
CrewMember.objects.get_or_create(crew=crew2, employee=e1, defaults={"role": "Командир"})

# Flight
f1, _ = Flight.objects.get_or_create(
    flight_number="SU-100",
    defaults={
        "route": r1, "aircraft": a1, "crew": crew1,
        "departure_dt": aware(2025, 1, 15, 10, 0),
        "arrival_dt": aware(2025, 1, 15, 11, 30),
        "tickets_sold": 150,
    },
)
f2, _ = Flight.objects.get_or_create(
    flight_number="SU-200",
    defaults={
        "route": r2, "aircraft": a3, "crew": crew2,
        "departure_dt": aware(2025, 1, 16, 12, 0),
        "arrival_dt": aware(2025, 1, 16, 13, 45),
        "tickets_sold": 95,
    },
)
f3, _ = Flight.objects.get_or_create(
    flight_number="SU-300",
    defaults={
        "route": r3, "aircraft": a1, "crew": crew1,
        "departure_dt": aware(2025, 1, 17, 8, 0),
        "arrival_dt": aware(2025, 1, 17, 10, 30),
        "tickets_sold": 180,
    },
)

# TransitStop (у рейса SU-300 транзит в Казани)
TransitStop.objects.get_or_create(
    flight=f3, airport=kzn,
    defaults={
        "arrival_dt": aware(2025, 1, 17, 9, 0),
        "departure_dt": aware(2025, 1, 17, 9, 30),
    },
)

# Admission
Admission.objects.get_or_create(
    employee=e1, flight=f1,
    defaults={"is_allowed": True, "issue_date": date(2025, 1, 10)},
)
Admission.objects.get_or_create(
    employee=e2, flight=f1,
    defaults={"is_allowed": True, "issue_date": date(2025, 1, 10)},
)
Admission.objects.get_or_create(
    employee=e1, flight=f3,
    defaults={"is_allowed": True, "issue_date": date(2025, 1, 12)},
)

print("CompanyType:", CompanyType.objects.count())
print("Company:", Company.objects.count())
print("AircraftType:", AircraftType.objects.count())
print("Aircraft:", Aircraft.objects.count())
print("Airport:", Airport.objects.count())
print("Route:", Route.objects.count())
print("Crew:", Crew.objects.count())
print("Employee:", Employee.objects.count())
print("Flight:", Flight.objects.count())
print("TransitStop:", TransitStop.objects.count())
print("CrewMember:", CrewMember.objects.count())
print("Admission:", Admission.objects.count())