from django.core.validators import MinValueValidator
from django.db import models


class PrintingHouse(models.Model):
    """Типография. Закрытая типография: is_active=False."""
    name = models.CharField('Название', max_length=200)
    address = models.CharField('Адрес', max_length=300)
    is_active = models.BooleanField('Работает', default=True)

    def __str__(self):
        return f'{self.name} ({self.address})'


class Newspaper(models.Model):
    """Газета."""
    title = models.CharField('Название', max_length=200)
    publication_index = models.CharField('Индекс издания', max_length=20, unique=True)
    editor_last_name = models.CharField('Фамилия редактора', max_length=100)
    editor_first_name = models.CharField('Имя редактора', max_length=100)
    editor_patronymic = models.CharField('Отчество редактора', max_length=100, blank=True)
    price = models.DecimalField('Цена экземпляра', max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    printing_houses = models.ManyToManyField(PrintingHouse, through='PrintRun', related_name='newspapers',
                                             verbose_name='Типографии')

    def __str__(self):
        return f'{self.title} ({self.publication_index})'


class PostOffice(models.Model):
    """Почтовое отделение."""
    number = models.CharField('Номер', max_length=20, unique=True)
    address = models.CharField('Адрес', max_length=300)

    def __str__(self):
        return f'№{self.number} ({self.address})'


class PrintRun(models.Model):
    """Тираж газеты в типографии."""
    printing_house = models.ForeignKey(PrintingHouse, on_delete=models.CASCADE, related_name='print_runs',
                                       verbose_name='Типография')
    newspaper = models.ForeignKey(Newspaper, on_delete=models.CASCADE, related_name='print_runs',
                                  verbose_name='Газета')
    circulation = models.PositiveIntegerField('Тираж', validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['printing_house', 'newspaper'], name='unique_print_run'),
        ]

    def __str__(self):
        return f'{self.newspaper} — {self.printing_house}: {self.circulation}'


class Delivery(models.Model):
    """Часть тиража, отправляемая в почтовое отделение."""
    print_run = models.ForeignKey(PrintRun, on_delete=models.CASCADE, related_name='deliveries',
                                  verbose_name='Тираж')
    post_office = models.ForeignKey(PostOffice, on_delete=models.CASCADE, related_name='deliveries',
                                    verbose_name='Почтовое отделение')
    quantity = models.PositiveIntegerField('Количество', validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['print_run', 'post_office'], name='unique_delivery'),
        ]

    def __str__(self):
        return f'{self.print_run} → {self.post_office}: {self.quantity}'
