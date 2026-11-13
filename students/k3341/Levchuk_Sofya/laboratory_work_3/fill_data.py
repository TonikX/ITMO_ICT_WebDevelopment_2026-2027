from datetime import date

from insurance_app.models import (
    Agent,
    EmploymentContract,
    Organization,
    Individual,
    RiskCategory,
    Contract,
    ContractTariff,
    InsuredPerson,
    InsuranceCase,
)


def main():
    # категории риска
    first = RiskCategory.objects.create(name='Первая')
    second = RiskCategory.objects.create(name='Вторая')
    top = RiskCategory.objects.create(name='Высшая')

    # страховые агенты
    # Иванов и Петров работают, Сидоров уволен (fire_date заполнен)
    ivanov = Agent.objects.create(
        first_name='Иван', last_name='Иванов', middle_name='Иванович',
        passport_series='1234', passport_number='567890',
        phone='79111111111', email='ivanov@insurance.ru',
    )
    petrov = Agent.objects.create(
        first_name='Петр', last_name='Петров', middle_name='Петрович',
        passport_series='2345', passport_number='678901',
        phone='79122222222', email='petrov@insurance.ru',
    )
    sidorov = Agent.objects.create(
        first_name='Сидор', last_name='Сидоров', middle_name='Сидорович',
        passport_series='3456', passport_number='789012',
        phone='79133333333', email='sidorov@insurance.ru',
    )

    # трудовые договоры агентов
    # пустой fire_date означает, что агент сейчас работает
    EmploymentContract.objects.create(agent=ivanov, hire_date=date(2020, 1, 15))
    EmploymentContract.objects.create(agent=petrov, hire_date=date(2021, 3, 1))
    EmploymentContract.objects.create(
        agent=sidorov, hire_date=date(2019, 5, 20), fire_date=date(2025, 11, 30),
    )

    # организации (реальные компании Санкт-Петербурга)
    medclinic = Organization.objects.create(
        code='MED-001',
        full_name='Акционерное общество «Медик»',
        short_name='АО «Медик»',
        address='г. Санкт-Петербург, 6-я линия В.О., д. 7',
        bank_number='40702810100000012345',
        specialization='Медицинское учреждение',
    )
    avtotrans = Organization.objects.create(
        code='AUTO-002',
        full_name='Государственное унитарное предприятие города Санкт-Петербурга «Пассажиравтотранс»',
        short_name='ГУП «Пассажиравтотранс»',
        address='г. Санкт-Петербург, Гражданский пр-т, д. 117',
        bank_number='40702810100000067890',
        specialization='Автотранспортное предприятие',
    )
    itmo = Organization.objects.create(
        code='EDU-003',
        full_name='Федеральное государственное автономное образовательное учреждение высшего образования «НИУ ИТМО»',
        short_name='Университет ИТМО',
        address='г. Санкт-Петербург, Кронверкский пр-т, д. 49',
        bank_number='40702810100000024680',
        specialization='Учебное заведение',
    )

    # физлица
    smirnov = Individual.objects.create(
        first_name='Александр', last_name='Смирнов', middle_name='Сергеевич',
        birth_date=date(1985, 4, 12),
    )
    kuznetsova = Individual.objects.create(
        first_name='Ольга', last_name='Кузнецова', middle_name='Дмитриевна',
        birth_date=date(1990, 9, 23),
    )
    vasiliev = Individual.objects.create(
        first_name='Василий', last_name='Васильев', middle_name='Васильевич',
        birth_date=date(1978, 2, 5),
    )
    novikov = Individual.objects.create(
        first_name='Артем', last_name='Новиков', middle_name='Олегович',
        birth_date=date(1992, 3, 18),
    )
    zaytseva = Individual.objects.create(
        first_name='Татьяна', last_name='Зайцева', middle_name='Николаевна',
        birth_date=date(1988, 5, 9),
    )
    sokolov = Individual.objects.create(
        first_name='Андрей', last_name='Соколов', middle_name='Игоревич',
        birth_date=date(1983, 12, 2),
    )
    morozov = Individual.objects.create(
        first_name='Сергей', last_name='Морозов', middle_name='Петрович',
        birth_date=date(1988, 11, 17),
    )
    volkova = Individual.objects.create(
        first_name='Елена', last_name='Волкова', middle_name='Юрьевна',
        birth_date=date(1992, 6, 25),
    )
    fyodorov = Individual.objects.create(
        first_name='Павел', last_name='Федоров', middle_name='Сергеевич',
        birth_date=date(1975, 8, 14),
    )
    popova = Individual.objects.create(
        first_name='Анна', last_name='Попова', middle_name='Владимировна',
        birth_date=date(1995, 7, 30),
    )

    # страховые договоры
    # K1 - коллективный, "Медик", агент Иванов, действует весь 2026 год
    k1 = Contract.objects.create(
        contract_type=Contract.COLLECTIVE,
        conclusion_date=date(2025, 12, 15),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        agent=ivanov, organization=medclinic,
    )
    # K2 - коллективный, "Пассажиравтотранс", агент Иванов
    k2 = Contract.objects.create(
        contract_type=Contract.COLLECTIVE,
        conclusion_date=date(2026, 2, 10),
        start_date=date(2026, 3, 1),
        end_date=date(2027, 2, 28),
        agent=ivanov, organization=avtotrans,
    )
    # K3 - коллективный, ИТМО, агент Петров
    k3 = Contract.objects.create(
        contract_type=Contract.COLLECTIVE,
        conclusion_date=date(2026, 1, 20),
        start_date=date(2026, 2, 1),
        end_date=date(2027, 1, 31),
        agent=petrov, organization=itmo,
    )
    # K4 - коллективный, ИТМО, агент Иванов, но просроченный (2024 год)
    k4 = Contract.objects.create(
        contract_type=Contract.COLLECTIVE,
        conclusion_date=date(2023, 12, 1),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        agent=ivanov, organization=itmo,
    )
    # I1 - индивидуальный, Морозов, агент Иванов
    i1 = Contract.objects.create(
        contract_type=Contract.INDIVIDUAL,
        conclusion_date=date(2026, 3, 25),
        start_date=date(2026, 4, 1),
        end_date=date(2027, 3, 31),
        agent=ivanov, individual=morozov,
    )
    # I2 - индивидуальный, Волкова, агент Петров
    i2 = Contract.objects.create(
        contract_type=Contract.INDIVIDUAL,
        conclusion_date=date(2026, 4, 20),
        start_date=date(2026, 5, 1),
        end_date=date(2027, 4, 30),
        agent=petrov, individual=volkova,
    )
    # I3 - индивидуальный, Федоров, агент Сидоров (уволен, но договор действует)
    i3 = Contract.objects.create(
        contract_type=Contract.INDIVIDUAL,
        conclusion_date=date(2026, 2, 25),
        start_date=date(2026, 3, 1),
        end_date=date(2027, 2, 28),
        agent=sidorov, individual=fyodorov,
    )

    # тарифы: сумма выплат по категории риска
    ContractTariff.objects.create(contract=k1, risk_category=first, payout_amount=150000)
    ContractTariff.objects.create(contract=k1, risk_category=second, payout_amount=250000)
    ContractTariff.objects.create(contract=k1, risk_category=top, payout_amount=300000)

    ContractTariff.objects.create(contract=k2, risk_category=first, payout_amount=180000)
    ContractTariff.objects.create(contract=k2, risk_category=second, payout_amount=200000)
    ContractTariff.objects.create(contract=k2, risk_category=top, payout_amount=350000)

    ContractTariff.objects.create(contract=k3, risk_category=first, payout_amount=200000)
    ContractTariff.objects.create(contract=k3, risk_category=second, payout_amount=220000)

    ContractTariff.objects.create(contract=k4, risk_category=first, payout_amount=100000)

    ContractTariff.objects.create(contract=i1, risk_category=top, payout_amount=500000)
    ContractTariff.objects.create(contract=i2, risk_category=second, payout_amount=250000)
    ContractTariff.objects.create(contract=i3, risk_category=first, payout_amount=120000)

    # застрахованные сотрудники
    # сотрудники коллективных договоров
    ip_smirnov = InsuredPerson.objects.create(contract=k1, individual=smirnov, risk_category=first)
    ip_kuznetsova = InsuredPerson.objects.create(contract=k1, individual=kuznetsova, risk_category=top)
    ip_vasiliev = InsuredPerson.objects.create(contract=k1, individual=vasiliev, risk_category=second)
    ip_novikov = InsuredPerson.objects.create(contract=k2, individual=novikov, risk_category=first)
    ip_zaytseva = InsuredPerson.objects.create(contract=k2, individual=zaytseva, risk_category=second)
    InsuredPerson.objects.create(contract=k3, individual=sokolov, risk_category=first)
    InsuredPerson.objects.create(contract=k3, individual=popova, risk_category=second)
    # в индивидуальном договоре застрахованным лицом является сам клиент
    ip_morozov = InsuredPerson.objects.create(contract=i1, individual=morozov, risk_category=top)
    InsuredPerson.objects.create(contract=i2, individual=volkova, risk_category=second)
    InsuredPerson.objects.create(contract=i3, individual=fyodorov, risk_category=first)

    # страховые случаи
    # сумма выплаты равна тарифу договора по категории сотрудника
    InsuranceCase.objects.create(
        insured_person=ip_smirnov, case_date=date(2026, 5, 20),
        reason='Производственная травма', decision=InsuranceCase.PAID, payout_amount=150000,
    )
    InsuranceCase.objects.create(
        insured_person=ip_kuznetsova, case_date=date(2026, 7, 14),
        reason='Тяжелое заболевание', decision=InsuranceCase.PAID, payout_amount=300000,
    )
    InsuranceCase.objects.create(
        insured_person=ip_novikov, case_date=date(2026, 3, 15),
        reason='Дорожно-транспортное происшествие', decision=InsuranceCase.PAID, payout_amount=180000,
    )
    InsuranceCase.objects.create(
        insured_person=ip_zaytseva, case_date=date(2026, 8, 2),
        reason='Дорожно-транспортное происшествие', decision=InsuranceCase.PAID, payout_amount=200000,
    )
    InsuranceCase.objects.create(
        insured_person=ip_morozov, case_date=date(2026, 9, 10),
        reason='Тяжелое заболевание', decision=InsuranceCase.PAID, payout_amount=500000,
    )
    # отказ в выплате: payout_amount не указываем - останется NULL
    InsuranceCase.objects.create(
        insured_person=ip_vasiliev, case_date=date(2026, 10, 5),
        reason='Бытовая травма', decision=InsuranceCase.DENIED,
    )

    print('Данные загружены:')
    print(f'  агентов: {Agent.objects.count()} (Сидоров уволен)')
    print(f'  трудовых договоров: {EmploymentContract.objects.count()}')
    print(f'  организаций: {Organization.objects.count()} ("Медик", "Пассажиравтотранс", ИТМО)')
    print(f'  физических лиц: {Individual.objects.count()}')
    print(f'  категорий риска: {RiskCategory.objects.count()}')
    print(f'  страховых договоров: {Contract.objects.count()} (K4 - просроченный)')
    print(f'  тарифов: {ContractTariff.objects.count()}')
    print(f'  застрахованных: {InsuredPerson.objects.count()}')
    print(f'  страховых случаев: {InsuranceCase.objects.count()} (один - отказ)')


main()