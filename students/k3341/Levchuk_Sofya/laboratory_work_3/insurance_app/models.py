from datetime import date

from django.db import models


class Agent(models.Model):
    """ страховой агент: ФИО, паспортные и контактные данные """

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    passport_series = models.CharField(max_length=10)
    passport_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()


class EmploymentContract(models.Model):
    """ трудовой договор со страховым агентом (прием и увольнение) """

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='employment_contracts',
    )
    hire_date = models.DateField()
    fire_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Трудовой договор с {self.agent} от {self.hire_date}'


class Organization(models.Model):
    """ организация (юридическое лицо), с которой заключен коллективный договор """

    code = models.CharField(max_length=20)
    full_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)
    bank_number = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.short_name or self.full_name


class Individual(models.Model):
    """ физическое лицо: клиент индивидуального договора или застрахованный сотрудник """

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField()

    @property
    def age(self):
        """ полных лет на сегодня, вычисляется при обращении и в базе не хранится """
        today = date.today()
        birthday_this_year = date(today.year, self.birth_date.month, self.birth_date.day)
        if birthday_this_year > today:
            return today.year - self.birth_date.year - 1
        return today.year - self.birth_date.year

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'.strip()


class RiskCategory(models.Model):
    """ категория риска (первая, вторая, высшая...) """

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Contract(models.Model):
    """ страховой договор: коллективный (с организацией) или индивидуальный (с физлицом) """

    INDIVIDUAL = 'individual'
    COLLECTIVE = 'collective'
    CONTRACT_TYPE_CHOICES = [
        (INDIVIDUAL, 'Индивидуальный'),
        (COLLECTIVE, 'Коллективный'),
    ]

    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)
    conclusion_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='contracts')
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='contracts',
        null=True, blank=True,
    )
    individual = models.ForeignKey(
        Individual, on_delete=models.CASCADE, related_name='contracts',
        null=True, blank=True,
    )

    def __str__(self):
        if self.contract_type == self.COLLECTIVE:
            return f'Коллективный договор №{self.id} - {self.organization}'
        return f'Индивидуальный договор №{self.id} - {self.individual}'


class ContractTariff(models.Model):
    """ тариф договора: сумма выплат по категории риска """

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='tariffs')
    risk_category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE, related_name='tariffs')
    payout_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.risk_category} - {self.payout_amount}'


class InsuredPerson(models.Model):
    """ застрахованный сотрудник в коллективном договоре """

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='insured_persons')
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE, related_name='insured_persons')
    risk_category = models.ForeignKey(RiskCategory, on_delete=models.CASCADE, related_name='insured_persons')

    def __str__(self):
        return f'{self.individual} ({self.risk_category})'


class InsuranceCase(models.Model):
    """ страховой случай по застрахованному сотруднику """

    PAID = 'paid'
    DENIED = 'denied'
    PENDING = 'pending'
    DECISION_CHOICES = [
        (PAID, 'Выплачено'),
        (DENIED, 'Отказано'),
        (PENDING, 'На рассмотрении'),
    ]

    insured_person = models.ForeignKey(InsuredPerson, on_delete=models.CASCADE, related_name='insurance_cases')
    case_date = models.DateField()
    reason = models.TextField(blank=True)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    payout_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'Страховой случай {self.case_date} - {self.insured_person}'