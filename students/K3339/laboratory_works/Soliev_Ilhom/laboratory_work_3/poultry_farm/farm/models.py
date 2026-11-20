from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class FarmUser(AbstractUser):
    ROLE_DIRECTOR = "director"
    ROLE_WORKER = "worker"
    ROLE_CHOICES = (
        (ROLE_DIRECTOR, "Директор"),
        (ROLE_WORKER, "Работник"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=ROLE_WORKER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        verbose_name = "учётная запись"
        verbose_name_plural = "учётные записи"

    def __str__(self):
        return self.username


class Season(models.TextChoices):
    WINTER = "winter", "Зима"
    SPRING = "spring", "Весна"
    SUMMER = "summer", "Лето"
    AUTUMN = "autumn", "Осень"


class ChickenRemovalReason(models.TextChoices):
    SOLD = "sold", "Продана"
    DECEASED = "deceased", "Пала"
    CULLED = "culled", "Выбракована"
    OTHER = "other", "Другая причина"


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="employee",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=200)
    passport_series = models.CharField(max_length=10)
    passport_number = models.CharField(max_length=20)
    passport_issued_by = models.TextField(blank=True)
    passport_issued_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("full_name", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("passport_series", "passport_number"),
                name="unique_employee_passport",
            ),
        ]
        verbose_name = "работник"
        verbose_name_plural = "работники"

    def __str__(self):
        return self.full_name


class EmploymentContract(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="contracts",
    )
    contract_number = models.CharField(max_length=50, unique=True)
    signed_at = models.DateField()
    started_at = models.DateField()
    ended_at = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    dismissal_reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-started_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(salary__gte=0), name="contract_salary_nonnegative"),
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gte=F("started_at")),
                name="contract_end_not_before_start",
            ),
        ]
        verbose_name = "трудовой договор"
        verbose_name_plural = "трудовые договоры"

    def clean(self):
        super().clean()
        if self.ended_at and self.ended_at < self.started_at:
            raise ValidationError({"ended_at": "Дата увольнения не может быть раньше даты начала работы."})
        if self.salary is not None and self.salary < 0:
            raise ValidationError({"salary": "Зарплата не может быть отрицательной."})

    def __str__(self):
        return self.contract_number


class Workshop(models.Model):
    workshop_number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    capacity_cages = models.PositiveIntegerField()

    class Meta:
        ordering = ("workshop_number",)
        constraints = [
            models.CheckConstraint(condition=Q(capacity_cages__gt=0), name="workshop_capacity_positive"),
        ]
        verbose_name = "цех"
        verbose_name_plural = "цехи"

    def clean(self):
        super().clean()
        if self.capacity_cages < 1:
            raise ValidationError({"capacity_cages": "Вместимость цеха должна быть больше нуля."})
        if self.pk and self.cages.count() > self.capacity_cages:
            raise ValidationError({"capacity_cages": "В цехе уже больше клеток, чем новая вместимость."})

    def __str__(self):
        return self.name or f"Цех № {self.workshop_number}"


class Cage(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="cages")
    row_number = models.PositiveIntegerField()
    cage_number = models.PositiveIntegerField()
    capacity_chickens = models.PositiveIntegerField()

    class Meta:
        ordering = ("workshop__workshop_number", "row_number", "cage_number")
        constraints = [
            models.UniqueConstraint(
                fields=("workshop", "row_number", "cage_number"),
                name="unique_cage_code_in_workshop",
            ),
            models.CheckConstraint(condition=Q(capacity_chickens__gt=0), name="cage_capacity_positive"),
        ]
        verbose_name = "клетка"
        verbose_name_plural = "клетки"

    def clean(self):
        super().clean()
        if self.capacity_chickens < 1:
            raise ValidationError({"capacity_chickens": "Вместимость клетки должна быть больше нуля."})
        if self.workshop_id:
            count = Cage.objects.filter(workshop_id=self.workshop_id).exclude(pk=self.pk).count()
            if count >= self.workshop.capacity_cages:
                raise ValidationError({"workshop": "В цехе достигнута вместимость по числу клеток."})
        if self.pk and self.chicken_assignments.filter(valid_to__isnull=True).count() > self.capacity_chickens:
            raise ValidationError({"capacity_chickens": "В клетке уже больше кур, чем новая вместимость."})

    def __str__(self):
        return f"Цех {self.workshop.workshop_number}, ряд {self.row_number}, клетка {self.cage_number}"


class Breed(models.Model):
    name = models.CharField(max_length=100, unique=True)
    average_eggs_per_month = models.PositiveIntegerField()
    average_weight_grams = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.CheckConstraint(condition=Q(average_eggs_per_month__gte=0), name="breed_eggs_nonnegative"),
            models.CheckConstraint(condition=Q(average_weight_grams__gte=0), name="breed_weight_nonnegative"),
        ]
        verbose_name = "порода"
        verbose_name_plural = "породы"

    def __str__(self):
        return self.name


class Chicken(models.Model):
    breed = models.ForeignKey(Breed, on_delete=models.PROTECT, related_name="chickens")
    birth_date = models.DateField()
    arrived_at = models.DateField()
    removed_at = models.DateField(null=True, blank=True)
    removal_reason = models.CharField(
        max_length=20,
        choices=ChickenRemovalReason.choices,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("id",)
        constraints = [
            models.CheckConstraint(condition=Q(birth_date__lte=F("arrived_at")), name="chicken_born_before_arrival"),
            models.CheckConstraint(
                condition=Q(removed_at__isnull=True) | Q(removed_at__gte=F("arrived_at")),
                name="chicken_removal_after_arrival",
            ),
        ]
        verbose_name = "курица"
        verbose_name_plural = "курицы"

    def clean(self):
        super().clean()
        if self.birth_date and self.arrived_at and self.birth_date > self.arrived_at:
            raise ValidationError({"birth_date": "Курица не может прибыть раньше даты рождения."})
        if self.removed_at and self.arrived_at and self.removed_at < self.arrived_at:
            raise ValidationError({"removed_at": "Дата выбытия не может быть раньше даты прибытия."})
        if self.removed_at and not self.removal_reason:
            raise ValidationError({"removal_reason": "Укажите причину выбытия курицы."})

    def __str__(self):
        return f"Курица № {self.pk} ({self.breed})"


class ChickenWeightRecord(models.Model):
    chicken = models.ForeignKey(Chicken, on_delete=models.CASCADE, related_name="weight_records")
    measured_at = models.DateField()
    weight_grams = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ("-measured_at", "chicken_id")
        constraints = [
            models.UniqueConstraint(fields=("chicken", "measured_at"), name="unique_chicken_weight_date"),
            models.CheckConstraint(condition=Q(weight_grams__gte=0), name="chicken_weight_nonnegative"),
        ]
        verbose_name = "измерение веса"
        verbose_name_plural = "измерения веса"

    def __str__(self):
        return f"Курица № {self.chicken_id}: {self.weight_grams} г ({self.measured_at})"


class ChickenCageAssignment(models.Model):
    chicken = models.ForeignKey(Chicken, on_delete=models.CASCADE, related_name="cage_assignments")
    cage = models.ForeignKey(Cage, on_delete=models.PROTECT, related_name="chicken_assignments")
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("chicken_id", "valid_from")
        constraints = [
            models.UniqueConstraint(fields=("chicken", "valid_from"), name="unique_chicken_assignment_start"),
            models.UniqueConstraint(
                fields=("chicken",),
                condition=Q(valid_to__isnull=True),
                name="one_open_cage_assignment_per_chicken",
            ),
            models.CheckConstraint(
                condition=Q(valid_to__isnull=True) | Q(valid_to__gte=F("valid_from")),
                name="cage_assignment_end_not_before_start",
            ),
        ]
        verbose_name = "назначение курицы в клетку"
        verbose_name_plural = "назначения кур в клетки"

    def clean(self):
        super().clean()
        if self.valid_to and self.valid_to < self.valid_from:
            raise ValidationError({"valid_to": "Дата окончания не может быть раньше даты начала."})
        if self.chicken_id:
            end = self.valid_to or models.DateField().to_python("9999-12-31")
            overlaps = ChickenCageAssignment.objects.filter(
                chicken_id=self.chicken_id,
                valid_from__lte=end,
            ).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=self.valid_from)).exclude(pk=self.pk)
            if overlaps.exists():
                raise ValidationError("У курицы уже есть назначение на пересекающийся период.")

    def __str__(self):
        return f"Курица № {self.chicken_id} — клетка № {self.cage_id} с {self.valid_from}"


class EmployeeCageAssignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="cage_assignments")
    cage = models.ForeignKey(Cage, on_delete=models.CASCADE, related_name="employee_assignments")
    assigned_from = models.DateField()
    assigned_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("employee_id", "assigned_from")
        constraints = [
            models.UniqueConstraint(
                fields=("employee", "cage", "assigned_from"),
                name="unique_employee_cage_assignment_start",
            ),
            models.CheckConstraint(
                condition=Q(assigned_to__isnull=True) | Q(assigned_to__gte=F("assigned_from")),
                name="employee_assignment_end_not_before_start",
            ),
        ]
        verbose_name = "назначение работника на клетку"
        verbose_name_plural = "назначения работников на клетки"

    def clean(self):
        super().clean()
        if self.assigned_to and self.assigned_to < self.assigned_from:
            raise ValidationError({"assigned_to": "Дата окончания не может быть раньше даты начала."})
        if self.employee_id and self.cage_id:
            end = self.assigned_to or models.DateField().to_python("9999-12-31")
            overlaps = EmployeeCageAssignment.objects.filter(
                employee_id=self.employee_id,
                cage_id=self.cage_id,
                assigned_from__lte=end,
            ).filter(Q(assigned_to__isnull=True) | Q(assigned_to__gte=self.assigned_from)).exclude(pk=self.pk)
            if overlaps.exists():
                raise ValidationError("Работник уже назначен на эту клетку в пересекающийся период.")

    def __str__(self):
        return f"{self.employee} — клетка № {self.cage_id} с {self.assigned_from}"


class EggProductionRecord(models.Model):
    chicken = models.ForeignKey(Chicken, on_delete=models.CASCADE, related_name="egg_records")
    production_date = models.DateField()
    eggs_count = models.PositiveIntegerField()

    class Meta:
        ordering = ("-production_date", "chicken_id")
        constraints = [
            models.UniqueConstraint(fields=("chicken", "production_date"), name="unique_chicken_egg_date"),
            models.CheckConstraint(condition=Q(eggs_count__gte=0), name="egg_count_nonnegative"),
        ]
        verbose_name = "запись о яйценоскости"
        verbose_name_plural = "записи о яйценоскости"

    def clean(self):
        super().clean()
        if self.chicken_id:
            chicken = self.chicken
            if self.production_date < chicken.arrived_at:
                raise ValidationError({"production_date": "Дата яйценоскости раньше прибытия курицы."})
            if chicken.removed_at and self.production_date > chicken.removed_at:
                raise ValidationError({"production_date": "Нельзя записать яйца после выбытия курицы."})

    def __str__(self):
        return f"{self.chicken} — {self.eggs_count} яиц ({self.production_date})"


class Diet(models.Model):
    diet_number = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    daily_cost_per_chicken = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("diet_number",)
        constraints = [
            models.CheckConstraint(condition=Q(daily_cost_per_chicken__gte=0), name="diet_cost_nonnegative"),
        ]
        verbose_name = "диета"
        verbose_name_plural = "диеты"

    def __str__(self):
        return self.diet_number


class BreedSeasonDiet(models.Model):
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, related_name="season_diets")
    diet = models.ForeignKey(Diet, on_delete=models.PROTECT, related_name="breed_seasons")
    season = models.CharField(max_length=10, choices=Season.choices)

    class Meta:
        ordering = ("breed__name", "season")
        constraints = [
            models.UniqueConstraint(fields=("breed", "season"), name="unique_diet_per_breed_season"),
        ]
        verbose_name = "диета породы по сезону"
        verbose_name_plural = "диеты пород по сезонам"

    def __str__(self):
        return f"{self.breed}: {self.get_season_display()} — {self.diet}"
