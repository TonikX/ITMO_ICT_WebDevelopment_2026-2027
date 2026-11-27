from django.db import models

EDUCATION_CHOICES = [
    ('primary', 'начальное'),
    ('secondary', 'среднее'),
    ('vocational', 'среднее специальное'),
    ('higher', 'высшее'),
]

VACANCY_STATE_CHOICES = [
    ('open', 'открыта'),
    ('offered', 'предложена соискателю'),
    ('closed', 'закрыта'),
]

EDUCATION_ORDER = {'primary': 1, 'secondary': 2, 'vocational': 3, 'higher': 4}

class Profession(models.Model):
    name = models.CharField('Название', max_length=120, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Applicant(models.Model):
    full_name = models.CharField('ФИО', max_length=150)
    birth_date = models.DateField('Дата рождения')
    passport = models.CharField('Паспорт', max_length=30, unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Электронная почта', blank=True)
    education = models.CharField('Образование', max_length=30, choices=EDUCATION_CHOICES)
    profession = models.ForeignKey(
        Profession, on_delete=models.CASCADE, related_name='applicants', verbose_name='Профессия',
    )
    grade = models.PositiveSmallIntegerField('Разряд', null=True, blank=True)
    experience_years = models.PositiveSmallIntegerField('Стаж (лет)', default=0)
    last_salary = models.DecimalField('Последняя зарплата', max_digits=10, decimal_places=2, null=True, blank=True)
    registered_at = models.DateField('Дата регистрации')

    class Meta:
        ordering = ['-registered_at', 'full_name']

    def __str__(self):
        return f'{self.full_name} ({self.profession})'

class WorkExperience(models.Model):
    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name='work_experiences', verbose_name='Соискатель',
    )
    company = models.CharField('Организация', max_length=150)
    position = models.CharField('Должность', max_length=120)
    started_at = models.DateField('Дата приёма')
    ended_at = models.DateField('Дата увольнения', null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name_plural = 'places of work'

    def __str__(self):
        return f'{self.company} — {self.position}'

class Employer(models.Model):
    name = models.CharField('Название', max_length=150)
    address = models.CharField('Адрес', max_length=200)
    contact_person = models.CharField('Контактное лицо', max_length=150)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Электронная почта', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Vacancy(models.Model):
    employer = models.ForeignKey(
        Employer, on_delete=models.CASCADE, related_name='vacancies', verbose_name='Работодатель',
    )
    profession = models.ForeignKey(
        Profession, on_delete=models.CASCADE, related_name='vacancies', verbose_name='Профессия',
    )
    education = models.CharField('Требуемое образование', max_length=30, choices=EDUCATION_CHOICES)
    min_experience = models.PositiveSmallIntegerField('Требуемый стаж (лет)', default=0)
    grade = models.PositiveSmallIntegerField('Требуемый разряд', null=True, blank=True)
    salary = models.DecimalField('Зарплата', max_digits=10, decimal_places=2)
    posted_at = models.DateField('Дата подачи')
    state = models.CharField('Состояние', max_length=20, choices=VACANCY_STATE_CHOICES, default='open')
    extra_info = models.TextField('Дополнительная информация', blank=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f'{self.profession} — {self.employer.name}'

class Benefit(models.Model):
    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name='benefits', verbose_name='Соискатель',
    )
    amount = models.DecimalField('Размер', max_digits=10, decimal_places=2)
    started_at = models.DateField('Дата начала выплаты')
    ended_at = models.DateField('Дата окончания выплаты', null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.applicant.full_name}: {self.amount} руб.'

    def is_active(self, on_date=None):
        from django.utils import timezone
        today = on_date or timezone.localdate()
        if self.started_at > today:
            return False
        return self.ended_at is None or today <= self.ended_at

class Course(models.Model):
    name = models.CharField('Название', max_length=150)
    profession = models.ForeignKey(
        Profession, on_delete=models.CASCADE, related_name='courses', verbose_name='Профессия',
    )
    started_at = models.DateField('Дата начала')
    ended_at = models.DateField('Дата окончания')

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.name} ({self.profession})'

class Enrollment(models.Model):
    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Соискатель',
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Курс',
    )
    enrolled_at = models.DateField('Дата записи')
    result_grade = models.PositiveSmallIntegerField('Полученный разряд', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['applicant', 'course'], name='one_enrollment_per_course'),
        ]
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.applicant.full_name} на курсе «{self.course.name}»'

class VacancyMatch(models.Model):
    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name='vacancy_matches', verbose_name='Соискатель',
    )
    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name='matches', verbose_name='Вакансия',
    )
    suggested_at = models.DateField('Дата предложения')
    accepted = models.BooleanField('Принял ли соискатель', default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['applicant', 'vacancy'], name='one_match_per_vacancy'),
        ]
        ordering = ['-suggested_at']
        verbose_name_plural = 'vacancy matches'

    def __str__(self):
        return f'{self.applicant.full_name} → {self.vacancy}'
