from django.db import models
from django.conf import settings

class CarOwner(models.Model):
    id_owner = models.AutoField(primary_key=True)
    surname = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='car_owner'
    )
    def __str__(self):
        return f"{self.surname} {self.name}"


class Automobile(models.Model):
    id_automobile = models.AutoField(primary_key=True)
    registration_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30)
    owners = models.ManyToManyField(
        CarOwner,
        through='Ownership',
        related_name='automobiles'
    )
    def __str__(self):
        return self.registration_number


class Ownership(models.Model):
    id_owner_auto = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        CarOwner,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ownerships"
    )
    automobile = models.ForeignKey(
        Automobile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ownerships"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class DriverLicense(models.Model):
    id_license = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        CarOwner,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="licenses"
    )
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10)
    issue_date = models.DateTimeField()


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    passport_number = models.CharField(max_length=20)
    home_address = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100)

    def __str__(self):
        return f"Профиль: {self.user.username}"