from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from clinic.models import (
    Appointment,
    Cabinet,
    Doctor,
    DoctorSchedule,
    Patient,
    Service,
)


DOCTORS_DATA = [
    {
        "last_name": "Смирнова",
        "first_name": "Анна",
        "middle_name": "Игоревна",
        "specialty": "Отоларинголог",
        "education": "СПбГМУ",
        "gender": Doctor.Gender.FEMALE,
        "birth_date": date(1985, 3, 12),
        "work_start": date(2015, 9, 1),
        "contract_number": "D-101",
        "days": [0, 1, 2, 3, 4],
        "cabinet": ("101", time(9, 0), time(18, 0), "1001"),
        "service": ("Приём отоларинголога", "2500.00"),
        "link_user": "doctor",
    },
    {
        "last_name": "Иванов",
        "first_name": "Пётр",
        "middle_name": "Сергеевич",
        "specialty": "Терапевт",
        "education": "ПСПбГМУ",
        "gender": Doctor.Gender.MALE,
        "birth_date": date(1978, 7, 22),
        "work_start": date(2010, 1, 15),
        "contract_number": "D-102",
        "days": [0, 2, 4],
        "cabinet": ("205", time(8, 30), time(17, 30), "1002"),
        "service": ("Приём терапевта", "1800.00"),
        "link_user": "doctor_therapist",
    },
    {
        "last_name": "Козлов",
        "first_name": "Дмитрий",
        "middle_name": "Алексеевич",
        "specialty": "Хирург",
        "education": "Военно-медицинская академия",
        "gender": Doctor.Gender.MALE,
        "birth_date": date(1982, 11, 5),
        "work_start": date(2012, 5, 20),
        "contract_number": "D-103",
        "days": [1, 3, 5],
        "cabinet": ("310", time(10, 0), time(19, 0), "1003"),
        "service": ("Консультация хирурга", "3200.00"),
    },
    {
        "last_name": "Волкова",
        "first_name": "Екатерина",
        "middle_name": "Павловна",
        "specialty": "Кардиолог",
        "education": "Первый СПбГМУ им. Павлова",
        "gender": Doctor.Gender.FEMALE,
        "birth_date": date(1980, 2, 14),
        "work_start": date(2014, 3, 1),
        "contract_number": "D-104",
        "days": [0, 1, 3, 4],
        "cabinet": ("112", time(9, 0), time(16, 0), "1004"),
        "service": ("Приём кардиолога", "2800.00"),
        "link_user": "doctor_cardio",
    },
    {
        "last_name": "Морозов",
        "first_name": "Андрей",
        "middle_name": "Викторович",
        "specialty": "Невролог",
        "education": "СЗГМУ им. Мечникова",
        "gender": Doctor.Gender.MALE,
        "birth_date": date(1975, 6, 30),
        "work_start": date(2008, 11, 12),
        "contract_number": "D-105",
        "days": [1, 2, 3, 4],
        "cabinet": ("220", time(10, 0), time(18, 0), "1005"),
        "service": ("Приём невролога", "2600.00"),
    },
    {
        "last_name": "Лебедева",
        "first_name": "Ольга",
        "middle_name": "Сергеевна",
        "specialty": "Офтальмолог",
        "education": "СПбГПМУ",
        "gender": Doctor.Gender.FEMALE,
        "birth_date": date(1988, 9, 8),
        "work_start": date(2016, 8, 20),
        "contract_number": "D-106",
        "days": [0, 2, 3, 5],
        "cabinet": ("118", time(9, 30), time(17, 0), "1006"),
        "service": ("Приём офтальмолога", "2300.00"),
    },
    {
        "last_name": "Новиков",
        "first_name": "Илья",
        "middle_name": "Романович",
        "specialty": "Дерматолог",
        "education": "РНИМУ им. Пирогова",
        "gender": Doctor.Gender.MALE,
        "birth_date": date(1990, 12, 1),
        "work_start": date(2018, 2, 5),
        "contract_number": "D-107",
        "days": [0, 1, 2, 4],
        "cabinet": ("130", time(11, 0), time(19, 0), "1007"),
        "service": ("Приём дерматолога", "2400.00"),
    },
    {
        "last_name": "Кузнецова",
        "first_name": "Марина",
        "middle_name": "Александровна",
        "specialty": "Эндокринолог",
        "education": "СПбГМУ",
        "gender": Doctor.Gender.FEMALE,
        "birth_date": date(1983, 4, 19),
        "work_start": date(2013, 6, 10),
        "contract_number": "D-108",
        "days": [0, 2, 4, 5],
        "cabinet": ("215", time(8, 0), time(15, 0), "1008"),
        "service": ("Приём эндокринолога", "2700.00"),
    },
    {
        "last_name": "Соколов",
        "first_name": "Никита",
        "middle_name": "Олегович",
        "specialty": "Гастроэнтеролог",
        "education": "ПСПбГМУ",
        "gender": Doctor.Gender.MALE,
        "birth_date": date(1986, 8, 25),
        "work_start": date(2017, 1, 16),
        "contract_number": "D-109",
        "days": [1, 2, 3, 4],
        "cabinet": ("240", time(9, 0), time(17, 30), "1009"),
        "service": ("Приём гастроэнтеролога", "2550.00"),
    },
    {
        "last_name": "Павлова",
        "first_name": "Дарья",
        "middle_name": "Ильинична",
        "specialty": "Гинеколог",
        "education": "СЗГМУ им. Мечникова",
        "gender": Doctor.Gender.FEMALE,
        "birth_date": date(1984, 1, 7),
        "work_start": date(2011, 9, 1),
        "contract_number": "D-110",
        "days": [0, 1, 3, 4],
        "cabinet": ("301", time(9, 0), time(18, 0), "1010"),
        "service": ("Приём гинеколога", "2900.00"),
    },
]


DEMO_USERNAMES = {
    "admin",
    "manager",
    "doctor",
    "doctor_therapist",
    "doctor_cardio",
    "patient",
}


class Command(BaseCommand):
    """
    seed_clinic

    Loads demo data for admin, doctor and patient roles.
    Keeps medical cards of non-demo users (e.g. manually registered).
    """

    help = "Seed clinic demo data"

    def handle(self, *args, **options):
        preserved_patients = [
            {
                "user_id": patient.user_id,
                "last_name": patient.last_name,
                "first_name": patient.first_name,
                "middle_name": patient.middle_name,
                "birth_date": patient.birth_date,
                "gender": patient.gender,
                "phone": patient.phone,
                "address": patient.address,
                "passport": patient.passport,
                "card_number": patient.card_number,
            }
            for patient in Patient.objects.exclude(user__isnull=True)
            .exclude(user__username__in=DEMO_USERNAMES)
            .select_related("user")
        ]

        Appointment.objects.all().delete()
        DoctorSchedule.objects.all().delete()
        Cabinet.objects.all().delete()
        Service.objects.all().delete()
        Patient.objects.all().delete()
        Doctor.objects.all().delete()

        admin_user, _ = User.objects.get_or_create(username="admin")
        admin_user.email = "admin@clinic.local"
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("admin123")
        admin_user.save()

        manager, _ = User.objects.get_or_create(username="manager")
        manager.email = "manager@clinic.local"
        manager.is_staff = True
        manager.is_superuser = False
        manager.set_password("manager123")
        manager.save()

        doctor_accounts = {}
        for username, password in (
            ("doctor", "doctor123"),
            ("doctor_therapist", "doctor123"),
            ("doctor_cardio", "doctor123"),
        ):
            account, _ = User.objects.get_or_create(username=username)
            account.email = f"{username}@clinic.local"
            account.is_staff = False
            account.set_password(password)
            account.save()
            doctor_accounts[username] = account

        patient_user, _ = User.objects.get_or_create(username="patient")
        patient_user.email = "patient@clinic.local"
        patient_user.is_staff = False
        patient_user.set_password("patient123")
        patient_user.save()

        doctors_by_specialty = {}
        services_by_specialty = {}
        cabinets = {}

        for item in DOCTORS_DATA:
            link = item.get("link_user")
            user = doctor_accounts.get(link) if link else None
            doctor = Doctor.objects.create(
                user=user,
                last_name=item["last_name"],
                first_name=item["first_name"],
                middle_name=item["middle_name"],
                specialty=item["specialty"],
                education=item["education"],
                gender=item["gender"],
                birth_date=item["birth_date"],
                work_start=item["work_start"],
                contract_number=item["contract_number"],
                contract_date=item["work_start"],
            )
            doctors_by_specialty[item["specialty"]] = doctor

            for weekday in range(7):
                DoctorSchedule.objects.create(
                    doctor=doctor,
                    weekday=weekday,
                    is_working=weekday in item["days"],
                )

            number, start, end, phone = item["cabinet"]
            cabinets[item["specialty"]] = Cabinet.objects.create(
                number=number,
                work_start=start,
                work_end=end,
                responsible=doctor,
                phone=phone,
            )

            service_name, price = item["service"]
            services_by_specialty[item["specialty"]] = Service.objects.create(
                name=service_name,
                specialty=item["specialty"],
                price=Decimal(price),
            )

        ent = doctors_by_specialty["Отоларинголог"]
        therapist = doctors_by_specialty["Терапевт"]
        surgeon = doctors_by_specialty["Хирург"]
        cardiologist = doctors_by_specialty["Кардиолог"]

        service_ent = services_by_specialty["Отоларинголог"]
        service_therapist = services_by_specialty["Терапевт"]
        service_surgery = services_by_specialty["Хирург"]
        service_cardio = services_by_specialty["Кардиолог"]

        cabinet_1 = cabinets["Отоларинголог"]
        cabinet_2 = cabinets["Терапевт"]

        patient_linked = Patient.objects.create(
            user=patient_user,
            last_name="Петрова",
            first_name="Мария",
            middle_name="Андреевна",
            birth_date=date(1995, 4, 18),
            gender=Patient.Gender.FEMALE,
            phone="+7-900-111-22-33",
            address="Санкт-Петербург, Невский пр., 10",
            passport="4010 123456",
            card_number="MC-001",
        )
        patient_old = Patient.objects.create(
            last_name="Сидоров",
            first_name="Игорь",
            middle_name="Николаевич",
            birth_date=date(1975, 9, 3),
            gender=Patient.Gender.MALE,
            phone="+7-900-444-55-66",
            address="Санкт-Петербург, Литейный пр., 5",
            passport="4005 654321",
            card_number="MC-002",
        )
        patient_ent = Patient.objects.create(
            last_name="Орлова",
            first_name="Елена",
            middle_name="Викторовна",
            birth_date=date(1990, 1, 25),
            gender=Patient.Gender.FEMALE,
            phone="+7-900-777-88-99",
            address="Санкт-Петербург, Садовая ул., 20",
            passport="4012 998877",
            card_number="MC-003",
        )

        now = timezone.now()
        Appointment.objects.create(
            patient=patient_linked,
            doctor=therapist,
            cabinet=cabinet_2,
            service=service_therapist,
            visited_at=now - timedelta(days=2, hours=3),
            diagnosis="ОРВИ",
            condition="Удовлетворительное",
            recommendations="Покой, обильное питьё",
            cost=service_therapist.price,
            is_paid=True,
        )
        Appointment.objects.create(
            patient=patient_ent,
            doctor=ent,
            cabinet=cabinet_1,
            service=service_ent,
            visited_at=now - timedelta(days=1, hours=1),
            diagnosis="Отит",
            condition="Средней тяжести",
            recommendations="Капли в ухо 7 дней",
            cost=service_ent.price,
            is_paid=True,
        )
        Appointment.objects.create(
            patient=patient_old,
            doctor=surgeon,
            cabinet=None,
            service=service_surgery,
            visited_at=now - timedelta(hours=5),
            diagnosis="Грыжа",
            condition="Стабильное",
            recommendations="Плановая операция",
            cost=service_surgery.price,
            is_paid=False,
        )
        Appointment.objects.create(
            patient=patient_linked,
            doctor=ent,
            cabinet=cabinet_1,
            service=service_ent,
            visited_at=datetime.combine(
                date.today(),
                time(11, 30),
                tzinfo=timezone.get_current_timezone(),
            ),
            diagnosis="Ринит",
            condition="Лёгкое",
            recommendations="Промывание носа",
            cost=service_ent.price,
            is_paid=False,
        )
        Appointment.objects.create(
            patient=patient_old,
            doctor=cardiologist,
            cabinet=cabinets["Кардиолог"],
            service=service_cardio,
            visited_at=now - timedelta(days=3),
            diagnosis="Гипертония",
            condition="Удовлетворительное",
            recommendations="Контроль давления",
            cost=service_cardio.price,
            is_paid=True,
        )

        restored = 0
        for item in preserved_patients:
            passport = item["passport"]
            card_number = item["card_number"]
            # Avoid unique clashes with freshly seeded demo patients.
            if Patient.objects.filter(passport=passport).exists():
                passport = f"{passport}-u{item['user_id']}"
            if Patient.objects.filter(card_number=card_number).exists():
                card_number = f"{card_number}-u{item['user_id']}"

            Patient.objects.update_or_create(
                user_id=item["user_id"],
                defaults={
                    "last_name": item["last_name"],
                    "first_name": item["first_name"],
                    "middle_name": item["middle_name"],
                    "birth_date": item["birth_date"],
                    "gender": item["gender"],
                    "phone": item["phone"],
                    "address": item["address"],
                    "passport": passport,
                    "card_number": card_number,
                },
            )
            restored += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Clinic demo data loaded: {len(DOCTORS_DATA)} doctors.",
            ),
        )
        if restored:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Restored {restored} non-demo medical card(s).",
                ),
            )
        self.stdout.write("admin / admin123              — админ")
        self.stdout.write("manager / manager123          — менеджер (staff)")
        self.stdout.write("doctor / doctor123            — ЛОР Смирнова")
        self.stdout.write("doctor_therapist / doctor123  — терапевт Иванов")
        self.stdout.write("doctor_cardio / doctor123     — кардиолог Волкова")
        self.stdout.write("patient / patient123          — пациент Петрова")
