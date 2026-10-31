from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Car(models.Model):
    gov_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True)

class CarOwner(models.Model):
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    cars = models.ManyToManyField(Car, through='Having')

class Having(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

class CarLicense(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10)
    date_of_issue = models.DateTimeField()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    passport_number = models.CharField(max_length=6)
    address = models.CharField(max_length=100)
    nationality = models.CharField(max_length=30)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()