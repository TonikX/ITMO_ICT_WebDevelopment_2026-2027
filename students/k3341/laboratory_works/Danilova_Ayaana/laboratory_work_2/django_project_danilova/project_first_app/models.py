from django.db import models


class Car(models.Model):
    number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=20)


class Driver(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField()

    car = models.ManyToManyField(Car, through='DriverCar')


class DriverLisence(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    received_at = models.DateField(null=False)


class DriverCar(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    started_at = models.DateField()
    ended_at = models.DateField()

