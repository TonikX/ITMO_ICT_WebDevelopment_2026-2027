from django.db import models


class ReadingHall(models.Model):
    hall_number = models.CharField(max_length=20, unique=True, verbose_name='Номер зала')
    name = models.CharField(max_length=120, verbose_name='Название')
    capacity = models.IntegerField(verbose_name='Вместимость')

    class Meta:
        verbose_name = 'Читальный зал'
        verbose_name_plural = 'Читальные залы'

    def __str__(self):
        return f'Зал {self.hall_number} ({self.name})'


class Reader(models.Model):
    EDUCATION_CHOICES = [
        ('primary', 'Начальное'),
        ('secondary', 'Среднее'),
        ('higher', 'Высшее'),
        ('degree', 'Учёная степень'),
    ]

    hall = models.ForeignKey(
        ReadingHall, on_delete=models.PROTECT,
        related_name='readers', verbose_name='Зал'
    )
    ticket_number = models.CharField(max_length=30, unique=True, verbose_name='Номер билета')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    middle_name = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    passport = models.CharField(max_length=20, unique=True, verbose_name='Паспорт')
    birth_date = models.DateField(verbose_name='Дата рождения')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    phone = models.CharField(max_length=30, verbose_name='Телефон')
    education = models.CharField(
        max_length=20, choices=EDUCATION_CHOICES, verbose_name='Образование'
    )
    academic_degree = models.CharField(max_length=100, blank=True, verbose_name='Учёная степень')
    registered_at = models.DateField(auto_now_add=True, verbose_name='Дата записи')
    re_registered_at = models.DateField(null=True, blank=True, verbose_name='Дата перерегистрации')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.ticket_number})'


class Book(models.Model):
    title = models.CharField(max_length=300, verbose_name='Название')
    authors = models.CharField(max_length=300, verbose_name='Авторы')
    publisher = models.CharField(max_length=200, verbose_name='Издательство')
    year = models.IntegerField(verbose_name='Год издания')
    section = models.CharField(max_length=120, verbose_name='Раздел')
    cipher = models.CharField(max_length=50, unique=True, verbose_name='Шифр')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'

    def __str__(self):
        return f'{self.title} — {self.authors}'


class BookCopy(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='copies', verbose_name='Книга'
    )
    hall = models.ForeignKey(
        ReadingHall, on_delete=models.CASCADE, related_name='copies', verbose_name='Зал'
    )
    quantity = models.IntegerField(default=0, verbose_name='Количество')

    class Meta:
        verbose_name = 'Экземпляры книги в зале'
        verbose_name_plural = 'Экземпляры книг'
        unique_together = ('book', 'hall')

    def __str__(self):
        return f'{self.book.title} в зале {self.hall.hall_number}: {self.quantity}'


class BookLoan(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name='loans', verbose_name='Книга'
    )
    reader = models.ForeignKey(
        Reader, on_delete=models.CASCADE, related_name='loans', verbose_name='Читатель'
    )
    hall = models.ForeignKey(
        ReadingHall, on_delete=models.CASCADE, related_name='loans', verbose_name='Зал'
    )
    issued_at = models.DateTimeField(verbose_name='Дата выдачи')
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата возврата')

    class Meta:
        verbose_name = 'Выдача книги'
        verbose_name_plural = 'Выдачи книг'

    def __str__(self):
        return f'{self.book.title} → {self.reader}'