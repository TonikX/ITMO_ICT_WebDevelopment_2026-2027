from datetime import date, timedelta
import os

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from clinic.models import (
    Cabinet,
    Doctor,
    MedicalCard,
    Patient,
    PriceList,
    User,
    Visit,
    WorkSchedule,
)


class Command(BaseCommand):
    help = "Seed demo clinic data"

    def handle(self, *args, **options):
        admin_password = os.environ.get("DEMO_ADMIN_PASSWORD")
        if not admin_password:
            raise CommandError("Задайте DEMO_ADMIN_PASSWORD в .env")

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "email": "admin@clinic.local",
            },
        )
        if created:
            admin.set_password(admin_password)
            admin.save()

        doc_user, created = User.objects.get_or_create(
            username="doctor1",
            defaults={"role": User.ROLE_DOCTOR, "email": "doctor1@clinic.local"},
        )
        if created:
            doc_user.set_password(admin_password)
            doc_user.save()

        lor_user, created = User.objects.get_or_create(
            username="doctor_lor",
            defaults={"role": User.ROLE_DOCTOR, "email": "lor@clinic.local"},
        )
        if created:
            lor_user.set_password(admin_password)
            lor_user.save()

        therapist, _ = Doctor.objects.get_or_create(
            last_name="Иванов",
            first_name="Пётр",
            specialty="терапевт",
            defaults={
                "user": doc_user,
                "middle_name": "Сергеевич",
                "education": "СПбГМУ",
                "gender": "M",
                "birth_date": date(1980, 5, 12),
                "hire_date": date(2010, 1, 15),
                "contract_info": "ТД-101",
            },
        )
        lor, _ = Doctor.objects.get_or_create(
            last_name="Смирнова",
            first_name="Анна",
            specialty="отоларинголог",
            defaults={
                "user": lor_user,
                "middle_name": "Игоревна",
                "education": "ПСбГМУ",
                "gender": "F",
                "birth_date": date(1985, 8, 20),
                "hire_date": date(2015, 3, 1),
                "contract_info": "ТД-205",
            },
        )

        p1, _ = Patient.objects.get_or_create(
            last_name="Козлов",
            first_name="Игорь",
            phone="+79001112233",
            defaults={
                "middle_name": "Алексеевич",
                "birth_date": date(1990, 2, 10),
                "gender": "M",
            },
        )
        p2, _ = Patient.objects.get_or_create(
            last_name="Орлова",
            first_name="Мария",
            phone="+79004445566",
            defaults={
                "middle_name": "Павловна",
                "birth_date": date(1995, 11, 3),
                "gender": "F",
            },
        )
        p3, _ = Patient.objects.get_or_create(
            last_name="Белов",
            first_name="Никита",
            phone="+79007778899",
            defaults={
                "birth_date": date(1985, 7, 7),
                "gender": "M",
            },
        )

        card1, _ = MedicalCard.objects.get_or_create(patient=p1, defaults={"opened_at": date(2020, 1, 10)})
        card2, _ = MedicalCard.objects.get_or_create(patient=p2, defaults={"opened_at": date(2021, 5, 5)})
        card3, _ = MedicalCard.objects.get_or_create(patient=p3, defaults={"opened_at": date(2019, 9, 1)})

        cab1, _ = Cabinet.objects.get_or_create(
            number="101",
            defaults={"schedule": "9:00-18:00", "responsible_doctor": therapist, "phone": "101"},
        )
        cab2, _ = Cabinet.objects.get_or_create(
            number="205",
            defaults={"schedule": "10:00-19:00", "responsible_doctor": lor, "phone": "205"},
        )

        price_t, _ = PriceList.objects.get_or_create(
            service_name="Приём терапевта",
            defaults={"specialty": "терапевт", "price": 2500},
        )
        price_l, _ = PriceList.objects.get_or_create(
            service_name="Приём отоларинголога",
            defaults={"specialty": "отоларинголог", "price": 3000},
        )

        today = date.today()
        for offset, working in ((0, True), (1, True), (2, False), (3, True)):
            WorkSchedule.objects.get_or_create(
                doctor=therapist,
                work_date=today + timedelta(days=offset),
                defaults={"is_working": working},
            )
            WorkSchedule.objects.get_or_create(
                doctor=lor,
                work_date=today + timedelta(days=offset),
                defaults={"is_working": working},
            )

        now = timezone.now()
        Visit.objects.get_or_create(
            medical_card=card1,
            doctor=therapist,
            visit_at=now - timedelta(days=2),
            defaults={
                "cabinet": cab1,
                "price_list": price_t,
                "diagnosis": "ОРВИ",
                "condition": "удовлетворительное",
                "recommendations": "покой, обильное питьё",
                "cost": price_t.price,
                "is_paid": True,
            },
        )
        Visit.objects.get_or_create(
            medical_card=card2,
            doctor=lor,
            visit_at=now - timedelta(days=1),
            defaults={
                "cabinet": cab2,
                "price_list": price_l,
                "diagnosis": "отит",
                "condition": "средней тяжести",
                "recommendations": "капли, контроль через неделю",
                "cost": price_l.price,
                "is_paid": True,
            },
        )
        Visit.objects.get_or_create(
            medical_card=card3,
            doctor=lor,
            visit_at=now,
            defaults={
                "cabinet": cab2,
                "price_list": price_l,
                "diagnosis": "ринит",
                "condition": "лёгкое",
                "recommendations": "промывание",
                "cost": price_l.price,
                "is_paid": False,
            },
        )
        Visit.objects.get_or_create(
            medical_card=card1,
            doctor=lor,
            visit_at=now - timedelta(hours=5),
            defaults={
                "cabinet": cab2,
                "price_list": price_l,
                "diagnosis": "фарингит",
                "condition": "удовлетворительное",
                "recommendations": "полоскание",
                "cost": price_l.price,
                "is_paid": True,
            },
        )

        self.stdout.write(
            f"doctors={Doctor.objects.count()} patients={Patient.objects.count()} visits={Visit.objects.count()}"
        )
