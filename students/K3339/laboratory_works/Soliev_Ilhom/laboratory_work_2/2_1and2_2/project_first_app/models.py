from django.db import models

class CarOwner(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    birth_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class DriverLicense(models.Model):
    owner = models.ForeignKey(
        CarOwner,
        on_delete=models.CASCADE,
        related_name="licenses",
    )
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10)
    issue_date = models.DateTimeField()

    def __str__(self):
        return self.license_number


class Car(models.Model):
    registration_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30)
    owners = models.ManyToManyField(
        CarOwner,
        through="Ownership",
        related_name="cars",
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(
        CarOwner,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner} — {self.car}"
