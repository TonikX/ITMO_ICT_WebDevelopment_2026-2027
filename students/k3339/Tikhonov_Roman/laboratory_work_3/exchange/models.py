from django.db import models


class Profession(models.Model):
    name = models.CharField("Название", max_length=128, unique=True)
    description = models.CharField("Описание", max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Education(models.Model):
    level = models.CharField("Уровень", max_length=32, unique=True)
    priority = models.IntegerField("Приоритет")

    def __str__(self):
        return self.level


class Employer(models.Model):
    name = models.CharField("Название организации", max_length=255, unique=True)
    address = models.CharField("Адрес", max_length=255)
    contact_person = models.CharField("Контактное лицо", max_length=128)
    phone = models.CharField("Телефон", max_length=20)
    email = models.CharField("Email", max_length=128)
    inn = models.CharField("ИНН", max_length=12, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    profession = models.ForeignKey(
        "Profession", on_delete=models.PROTECT, related_name="courses", verbose_name="Профессия"
    )
    name = models.CharField("Название", max_length=255, unique=True)
    description = models.CharField("Программа", max_length=1000, blank=True, null=True)
    duration_hours = models.IntegerField("Длительность, часов")

    def __str__(self):
        return self.name


class Applicant(models.Model):
    last_name = models.CharField("Фамилия", max_length=64)
    first_name = models.CharField("Имя", max_length=64)
    middle_name = models.CharField("Отчество", max_length=64, blank=True, null=True)
    passport_number = models.CharField("Номер паспорта", max_length=20, unique=True)
    date_of_birth = models.DateField("Дата рождения")
    address = models.CharField("Адрес", max_length=255)
    phone = models.CharField("Телефон", max_length=20)
    email = models.CharField("Email", max_length=128, blank=True, null=True)
    profession = models.ForeignKey(
        "Profession", on_delete=models.PROTECT, related_name="applicants", verbose_name="Профессия"
    )
    education = models.ForeignKey(
        "Education", on_delete=models.PROTECT, related_name="applicants", verbose_name="Образование"
    )
    experience_years = models.IntegerField("Стаж, лет")
    rank = models.IntegerField("Разряд")
    last_salary = models.DecimalField("Последняя зарплата", max_digits=10, decimal_places=2)

    def __str__(self):
        return "{} {}".format(self.last_name, self.first_name)


class Vacancy(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыта"
        CLOSED = "closed", "Закрыта"

    employer = models.ForeignKey(
        "Employer", on_delete=models.PROTECT, related_name="vacancies", verbose_name="Работодатель"
    )
    profession = models.ForeignKey(
        "Profession", on_delete=models.PROTECT, related_name="vacancies", verbose_name="Профессия"
    )
    education = models.ForeignKey(
        "Education", on_delete=models.PROTECT, related_name="vacancies", verbose_name="Образование"
    )
    required_experience = models.IntegerField("Требуемый стаж, лет")
    required_rank = models.IntegerField("Требуемый разряд")
    salary_min = models.DecimalField("Зарплата от", max_digits=10, decimal_places=2)
    salary_max = models.DecimalField("Зарплата до", max_digits=10, decimal_places=2)
    status = models.CharField(
        "Состояние", max_length=16, choices=Status.choices, default=Status.OPEN
    )
    submission_date = models.DateField("Дата подачи")
    description = models.CharField("Описание", max_length=1000, blank=True, null=True)

    def __str__(self):
        return "{} @ {}".format(self.profession, self.employer)


class CourseEnrollment(models.Model):
    applicant = models.ForeignKey(
        "Applicant", on_delete=models.CASCADE, related_name="enrollments", verbose_name="Соискатель"
    )
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="enrollments", verbose_name="Курс"
    )
    completion_date = models.DateField("Дата завершения", blank=True, null=True)
    resulting_rank = models.IntegerField("Полученный разряд", blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["applicant", "course"], name="unique_applicant_course"
            )
        ]

    def __str__(self):
        return "{} - {}".format(self.applicant, self.course)


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Рассматривается"
        ACCEPTED = "accepted", "Принята"
        REJECTED = "rejected", "Отклонена"

    applicant = models.ForeignKey(
        "Applicant", on_delete=models.CASCADE, related_name="applications", verbose_name="Соискатель"
    )
    vacancy = models.ForeignKey(
        "Vacancy", on_delete=models.CASCADE, related_name="applications", verbose_name="Вакансия"
    )
    offer_date = models.DateField("Дата предложения", blank=True, null=True)
    status = models.CharField(
        "Статус", max_length=16, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["applicant", "vacancy"], name="unique_applicant_vacancy"
            )
        ]

    def __str__(self):
        return "{} -> {}".format(self.applicant, self.vacancy)


class Allowance(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Выплачивается"
        STOPPED = "stopped", "Прекращено"

    applicant = models.ForeignKey(
        "Applicant", on_delete=models.CASCADE, related_name="allowances", verbose_name="Соискатель"
    )
    allowance_no = models.IntegerField("Номер пособия")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", blank=True, null=True)
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    status = models.CharField(
        "Статус", max_length=16, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["applicant", "allowance_no"], name="unique_applicant_allowance"
            )
        ]

    def __str__(self):
        return "{} #{}".format(self.applicant, self.allowance_no)
