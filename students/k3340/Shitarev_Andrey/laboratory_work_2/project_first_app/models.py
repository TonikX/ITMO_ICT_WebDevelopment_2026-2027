from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    team = models.CharField(max_length=100)
    car_description = models.TextField()
    description = models.TextField()
    experience = models.CharField(max_length=100)
    driver_class = models.CharField(max_length=100)
    def __str__(self):
        return self.full_name

class Race(models.Model):
    name = models.CharField(max_length=150)
    date = models.DateField()
    place = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Registration(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    note = models.CharField(max_length=200, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['driver', 'race'], name='unique_driver_race')]
    def __str__(self):
        return f'{self.driver} — {self.race}'

class Run(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='runs')
    date = models.DateField()
    duration = models.DurationField()
    place = models.PositiveIntegerField(validators=[MinValueValidator(1)])

class Comment(models.Model):
    TYPES = [('cooperation', 'Вопрос о сотрудничестве'), ('racing', 'Вопрос о гонках'), ('other', 'Иное')]
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='comments')
    run_date = models.DateField()
    text = models.TextField()
    comment_type = models.CharField(max_length=20, choices=TYPES)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
