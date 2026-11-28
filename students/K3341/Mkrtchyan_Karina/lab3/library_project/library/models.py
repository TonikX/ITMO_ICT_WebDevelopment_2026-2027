from django.db import models
from django.core.validators import MinValueValidator


# Таблицы-справочники

class ReadingRoom(models.Model):
    """ Таблица ReadingRoom - хранит информацию о залах (id, номер, название и вместимость) """
    id_room = models.BigAutoField(primary_key=True)
    room_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'reading_room'

    def __str__(self):
        return f"{self.room_number} — {self.name}"


class Section(models.Model):
    """ Таблица Section - хранит информацию о разделах (id, название) """
    id_section = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'section'

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """ Таблица Publisher - хранит информацию об издательствах (id, название)

        ! Поле name сейчас не является уникальным
        (ex: двух разных городах могут быть издательства с одинаковыми названиями)
    """
    id_publisher = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'publisher'

    def __str__(self):
        return self.name


class Author(models.Model):
    """ Таблица Author - хранит информацию об авторах книг (id, полное имя) """
    id_author = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=200)

    class Meta:
        db_table = 'author'

    def __str__(self):
        return self.full_name


# Книги

class Book(models.Model):
    """ Таблица Book - хранит информацию о книгах (id, название, издательство, раздел, год издания)
        ! authors - это имя связи книги с авторами через таблицу BookAuthor (book.authors.all() - их получение)
     """
    id_book = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=300)
    publisher = models.ForeignKey(Publisher, on_delete=models.PROTECT, db_column='id_publisher', related_name='books')
    section = models.ForeignKey(Section, on_delete=models.PROTECT, db_column='id_section', related_name='books')
    publication_year = models.SmallIntegerField()

    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')

    class Meta:
        db_table = 'book'

    def __str__(self):
        return self.title


class BookAuthor(models.Model):
    """ Таблица BookAuthor - хранит связи книг с авторами по id (реализует отношение many-to-many) """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='id_book', related_name='book_authors')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_column='id_author', related_name='book_authors')

    class Meta:
        db_table = 'book_author'
        unique_together = (('book', 'author'),)


class BookCipherHistory(models.Model):
    """ Таблица BookCipherHistory - хранит информацию об изменениях шифров книг
        (id записи, id книги, новый шифр, даты начала и конца дейтсвия шифра) """
    id_cipher_hist = models.BigAutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='id_book', related_name='cipher_history')
    cipher = models.CharField(max_length=50)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'book_cipher_history'

    def save(self, *args, **kwargs):
        # автоматически закрываем предыдущую активную запись
        if self._state.adding:
            BookCipherHistory.objects.filter(book=self.book, valid_to__isnull=True, valid_from__lt=self.valid_from).update(valid_to=self.valid_from)
        super().save(*args, **kwargs)


# Экземпляры

class BookCopy(models.Model):
    """ Таблица BookCopy - хранит информацию о физических экземплярах книг
        (id, id книги, инвентарный номер экземпляра, дата поступления в фонд, статус экземпляра) """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'В фонде'
        WRITTEN_OFF = 'WRITTEN_OFF', 'Списан'
        LOST = 'LOST', 'Утерян'

    id_copy = models.BigAutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.PROTECT, db_column='id_book', related_name='copies')
    inventory_no = models.CharField(max_length=40, unique=True)
    acquired_at = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = 'book_copy'

    def __str__(self):
        return self.inventory_no


class CopyRoomHistory(models.Model):
    """ Таблица CopyRoomHistory - хранит информацию о размещении физических экземпляров книг
        (id, id экземпляра, id зала, дата начала и конца размещения экземпляра) """
    id_location = models.BigAutoField(primary_key=True)
    copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, db_column='id_copy', related_name='room_history')
    room = models.ForeignKey(ReadingRoom, on_delete=models.PROTECT, db_column='id_room', related_name='copy_history')
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'copy_room_history'

    def save(self, *args, **kwargs):
        if self._state.adding:
            CopyRoomHistory.objects.filter(copy=self.copy, valid_to__isnull=True, valid_from__lt=self.valid_from).update(valid_to=self.valid_from)
        super().save(*args, **kwargs)


# Читатели

class Reader(models.Model):
    """ Таблица Reader - хранит информацию о читателях
        (id, номер паспорта, имя, дата рождения, адрес, телефон, уровень образования, наличие ученой степени,
        дата регистрации, дата последнего изменения, дата исключения из числа действующих читателей) """

    class Education(models.TextChoices):
        PRIMARY = 'PRIMARY', 'Начальное'
        SECONDARY = 'SECONDARY', 'Среднее'
        VOCATIONAL = 'VOCATIONAL', 'Среднее специальное'
        HIGHER = 'HIGHER', 'Высшее'
        OTHER = 'OTHER', 'Другое'

    id_reader = models.BigAutoField(primary_key=True)
    passport_no = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField()
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=30, null=True, blank=True)
    education = models.CharField(max_length=30, choices=Education.choices)
    has_degree = models.BooleanField(default=False)
    registered_at = models.DateField()
    last_regeq_at = models.DateField()
    deregistered_at = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'reader'

    def save(self, *args, **kwargs):
        if self._state.adding and not self.last_regeq_at:
            self.last_regeq_at = self.registered_at  # при регистрации дата последнего изменения равна дате регистрации
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class ReaderTicketHistory(models.Model):
    """ Таблица ReaderTicketHistory - хранит историю изменений читательских билетов
        (id, id читателя, номер билета, даты начала и окончания действия билета )"""
    id_ticket_hist = models.BigAutoField(primary_key=True)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, db_column='id_reader', related_name='ticket_history')
    ticket_no = models.CharField(max_length=30, unique=True)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'reader_ticket_history'

    def save(self, *args, **kwargs):
        if self._state.adding:
            ReaderTicketHistory.objects.filter(
                reader=self.reader, valid_to__isnull=True, valid_from__lt=self.valid_from
            ).update(valid_to=self.valid_from)
        super().save(*args, **kwargs)


class ReaderRoomHistory(models.Model):
    """ Таблица ReaderRoomHistory - хранит историю читальных залов
        (id записи закрепления, id читателя, id зала, даты начала и окнчания закрепления) """
    id_reader_room = models.BigAutoField(primary_key=True)
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, db_column='id_reader', related_name='room_history')
    room = models.ForeignKey(ReadingRoom, on_delete=models.PROTECT, db_column='id_room', related_name='reader_history')
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'reader_room_history'

    def save(self, *args, **kwargs):
        if self._state.adding:
            ReaderRoomHistory.objects.filter(
                reader=self.reader, valid_to__isnull=True, valid_from__lt=self.valid_from
            ).update(valid_to=self.valid_from)
        super().save(*args, **kwargs)


# Выдача

class Loan(models.Model):
    """ Таблица Loan - хранит информацию о выдаче книг читателям
        (id, id экземпляра, id читателя, дата выдачи, плановая дата возврата, фактическая дата возврата) """
    id_loan = models.BigAutoField(primary_key=True)
    copy = models.ForeignKey(BookCopy, on_delete=models.PROTECT, db_column='id_copy', related_name='loans')
    reader = models.ForeignKey(Reader, on_delete=models.PROTECT, db_column='id_reader', related_name='loans')
    issued_at = models.DateTimeField()
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'loan'

    def __str__(self):
        return f"Loan #{self.id_loan}"
