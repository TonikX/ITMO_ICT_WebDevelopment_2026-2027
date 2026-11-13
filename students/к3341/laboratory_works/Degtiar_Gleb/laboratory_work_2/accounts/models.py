from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    address = models.CharField('Домашний адрес', max_length=255, blank=True)
    nationality = models.CharField('Национальность', max_length=80, blank=True)
    def __str__(self):
        return self.get_full_name() or self.username
