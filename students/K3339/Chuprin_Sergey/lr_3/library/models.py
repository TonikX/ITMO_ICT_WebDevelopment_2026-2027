from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=200)


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Book(models.Model):
    name = models.CharField(max_length=200)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    year_of_publication = models.PositiveIntegerField(
        validators=[MinValueValidator(1400), MaxValueValidator(2026)],
    )
    category = models.ManyToManyField(Category)
    code = models.CharField(max_length=100, unique=True)

    authors = models.ManyToManyField(Author)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    year_of_publication__gte=1400,
                    year_of_publication__lte=2026
                ),
                name="year_of_publication_range"
            )
        ]


class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    scrapped_at = models.DateField(
        null=True,
        blank=True
    )


class Reader(models.Model):
    class Education(models.TextChoices):
        PRIMARY = "primary", "Начальное"
        SECONDARY = "secondary", "Среднее"
        HIGHER = "higher", "Высшее"

    library_card_number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    passport_number = models.CharField(max_length=6,
                                       validators=[RegexValidator(r'^[0-9]{6}$')]
                                       )
    passport_series = models.CharField(max_length=4,
                                       validators=[RegexValidator(r'^[0-9]{4}$')]
                                       )
    date_of_birth = models.DateField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    education = models.CharField(
        max_length=20,
        choices=Education.choices,
    )
    has_academic_degree = models.BooleanField(default=False)
    last_registration_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["passport_series", "passport_number"],
                name="unique_reader_passport",
            )
        ]


class ReaderRoom(models.Model):
    name = models.CharField(max_length=200)
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()


class Loan(models.Model):
    book_copy = models.ForeignKey(BookCopy, on_delete=models.PROTECT)
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT)
    issued_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)


class ReaderRoomHistory(models.Model):
    class Reason(models.TextChoices):
        REGISTRATION = "registration", "Запись в библиотеку"
        TRANSFER = "transfer", "Перевод из другого зала"

    reader = models.ForeignKey(Reader, on_delete=models.PROTECT)
    reader_room = models.ForeignKey(ReaderRoom, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    reason = models.CharField(
        max_length=50,
        choices=Reason.choices,
    )



class BookCopyRoomHistory(models.Model):
    book_copy = models.ForeignKey(BookCopy, on_delete=models.PROTECT)
    reader_room = models.ForeignKey(ReaderRoom, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)