from __future__ import annotations

import os
from datetime import date, timedelta
import django

# Инициализируем окружение Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from django.utils import timezone
from flights.models import (
    Flight,
    FlightType,
    Passenger,
    Passport,
    Reservation,
    Review,
    Ticket,
    User,
)


@transaction.atomic
def run_seed() -> None:
    print("Начинаем заполнение базы данных тестовыми данными...")

    if User.objects.filter(username="admin").exists():
        print("База уже содержит данные! Сначала запустите .\\reset_db.ps1")
        return

    # ==========================================
    # 1. ПОЛЬЗОВАТЕЛИ (Админ, Работник, 3 Клиента)
    # ==========================================
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@airport.ru",
        password="Password123!",
        first_name="Алексей",
        last_name="Главный",
        phone_number="+79990000001",
    )

    worker = User.objects.create_user(
        username="worker",
        email="staff@airport.ru",
        password="Password123!",
        first_name="Елена",
        last_name="Диспетчерова",
        phone_number="+79990000002",
        is_staff=True,  # Сотрудник аэропорта (для проверки прав is_staff на клиенте)
    )

    user1 = User.objects.create_user(
        username="ivan_petrov",
        email="ivan@mail.ru",
        password="Password123!",
        first_name="Иван",
        last_name="Петров",
        phone_number="+79111112233",
    )

    user2 = User.objects.create_user(
        username="anna_smirnova",
        email="anna@yandex.ru",
        password="Password123!",
        first_name="Анна",
        last_name="Смирнова",
        phone_number="+79212223344",
    )

    user3 = User.objects.create_user(
        username="alex_volkov",
        email="volkov@gmail.com",
        password="Password123!",
        first_name="Александр",
        last_name="Волков",
        phone_number="+79313334455",
    )
    print(" -> Созданы пользователи: admin, worker и 3 клиента (пароль: Password123!).")

    # ==========================================
    # 2. СЕМЬИ (ПАССАЖИРЫ) И ИХ ПАСПОРТА
    # ==========================================
    # --- Семья 1: Петровы (у них УЖЕ БУДЕТ бронь и билеты) ---
    p_ivan = Passenger.objects.create(
        owner=user1, first_name="Иван", last_name="Петров", birth_date=date(1985, 5, 14)
    )
    Passport.objects.create(passenger=p_ivan, passport_number="4005 111222", is_active=False)
    Passport.objects.create(passenger=p_ivan, passport_number="4025 999888", is_active=True)

    p_maria = Passenger.objects.create(
        owner=user1, first_name="Мария", last_name="Петрова", birth_date=date(1988, 8, 22)
    )
    Passport.objects.create(passenger=p_maria, passport_number="4012 345678", is_active=True)

    p_dima = Passenger.objects.create(
        owner=user1, first_name="Дмитрий", last_name="Петров", birth_date=date(2015, 3, 10)
    )
    Passport.objects.create(passenger=p_dima, passport_number="IV-АК 654321", is_active=True)

    # --- Семья 2: Смирновы (БЕЗ броней — для ручного резервирования через сайт) ---
    p_anna = Passenger.objects.create(
        owner=user2, first_name="Анна", last_name="Смирнова", birth_date=date(1992, 11, 3)
    )
    Passport.objects.create(passenger=p_anna, passport_number="4515 777666", is_active=True)

    p_oleg = Passenger.objects.create(
        owner=user2, first_name="Олег", last_name="Смирнов", birth_date=date(1990, 1, 19)
    )
    Passport.objects.create(passenger=p_oleg, passport_number="4510 555444", is_active=True)

    # --- Семья 3: Волковы (БЕЗ броней — для ручного резервирования через сайт) ---
    p_alex = Passenger.objects.create(
        owner=user3, first_name="Александр", last_name="Волков", birth_date=date(1979, 7, 7)
    )
    Passport.objects.create(passenger=p_alex, passport_number="4102 888999", is_active=True)

    p_elena = Passenger.objects.create(
        owner=user3, first_name="Елена", last_name="Волкова", birth_date=date(1982, 4, 15)
    )
    Passport.objects.create(passenger=p_elena, passport_number="4105 222333", is_active=True)

    p_sofa = Passenger.objects.create(
        owner=user3, first_name="София", last_name="Волкова", birth_date=date(2018, 12, 1)
    )
    Passport.objects.create(passenger=p_sofa, passport_number="V-БМ 123789", is_active=True)

    print(" -> Созданы пассажиры (семьи) и паспорта для всех клиентов.")

    # ==========================================
    # 3. РЕЙСЫ (14 штук — чтобы сразу работала пагинация по 10 элементов и фильтры)
    # ==========================================
    now = timezone.now().replace(minute=0, second=0, microsecond=0)

    flights_data = [
        ("SU-1024", "Аэрофлот", 2, 4, 8, FlightType.DEPARTURE, "A12", 150),
        ("S7-2048", "S7 Airlines", 3, 10, 13, FlightType.DEPARTURE, "B04", 120),
        ("DP-404", "Победа", 5, 6, 9, FlightType.DEPARTURE, "C01", 150),
        ("UT-512", "UTair", 1, 2, 5, FlightType.ARRIVAL, "A05", 100),
        ("FV-6301", "Россия", 4, 12, 14, FlightType.ARRIVAL, "D08", 150),
        ("SU-1100", "Аэрофлот", 6, 8, 11, FlightType.DEPARTURE, "A10", 150),
        ("U6-305", "Уральские авиалинии", 7, 14, 18, FlightType.DEPARTURE, "B11", 140),
        ("5N-242", "Smartavia", 8, 9, 12, FlightType.ARRIVAL, "C03", 130),
        ("S7-1015", "S7 Airlines", 9, 15, 19, FlightType.ARRIVAL, "B02", 120),
        ("DP-201", "Победа", 10, 7, 10, FlightType.DEPARTURE, "C04", 150),
        ("FV-6002", "Россия", 11, 16, 18, FlightType.DEPARTURE, "D01", 150),
        ("UT-700", "UTair", 12, 11, 15, FlightType.ARRIVAL, "A03", 100),
        ("U6-812", "Уральские авиалинии", 13, 5, 9, FlightType.ARRIVAL, "B09", 140),
        ("SU-1550", "Аэрофлот", 14, 19, 23, FlightType.DEPARTURE, "A15", 150),
    ]

    created_flights: list[Flight] = []
    for num, airline, days_offset, dep_h, arr_h, f_type, gate, cap in flights_data:
        flight = Flight.objects.create(
            flight_number=num,
            airline=airline,
            departure=now + timedelta(days=days_offset, hours=dep_h),
            arrival=now + timedelta(days=days_offset, hours=arr_h),
            flight_type=f_type,
            gate=gate,
            capacity=cap,
        )
        created_flights.append(flight)

    flight1 = created_flights[0]  # SU-1024
    flight2 = created_flights[1]  # S7-2048
    print(f" -> Создано {len(created_flights)} рейсов (для демонстрации пагинации и фильтрации).")

    # ==========================================
    # 4. БРОНИРОВАНИЕ И БИЛЕТЫ (Для Ивана Петрова и его семьи)
    # ==========================================
    res_petrov = Reservation.objects.create(
        purchaser=user1,
        flight=flight1,
    )

    # Двое взрослых уже зарегистрированы на рейс сотрудником (с номерами билетов),
    # а ребенок еще ожидает регистрации (отлично для демонстрации работы сотрудника!).
    Ticket.objects.create(
        reservation=res_petrov,
        flight=flight1,
        passenger=p_ivan,
        seat_number=12,
        ticket_number="SU-555000101",
        is_checked_in=True,
    )
    Ticket.objects.create(
        reservation=res_petrov,
        flight=flight1,
        passenger=p_maria,
        seat_number=13,
        ticket_number="SU-555000102",
        is_checked_in=True,
    )
    Ticket.objects.create(
        reservation=res_petrov,
        flight=flight1,
        passenger=p_dima,
        seat_number=14,
        ticket_number="",
        is_checked_in=False,
    )
    print(" -> Создана 1 бронь и 3 билета для семьи Ивана Петрова на рейс SU-1024.")

    # ==========================================
    # 5. ОТЗЫВЫ (Рейтинг по шкале 1-10 согласно варианту задания)
    # ==========================================
    Review.objects.create(
        flight=flight1,
        author=user1,
        rating=10,
        text="Отличный рейс! Персонал вежливый, взлетели строго по расписанию.",
        flight_date=(now - timedelta(days=10)).date(),
    )
    Review.objects.create(
        flight=flight2,
        author=user2,
        rating=8,
        text="Всё хорошо, но у гейта B04 было мало свободных кресел для ожидания.",
        flight_date=(now - timedelta(days=5)).date(),
    )
    Review.objects.create(
        flight=flight1,
        author=user3,
        rating=9,
        text="Очень мягкая посадка, удобный шаг кресел.",
        flight_date=(now - timedelta(days=3)).date(),
    )
    print(" -> Добавлены тестовые отзывы (шкала 1–10).")
    print("\nУСПЕШНО! База данных полностью готова к работе.")


if __name__ == "__main__":
    run_seed()