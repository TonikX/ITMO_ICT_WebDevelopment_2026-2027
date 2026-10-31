from django.db import models
from django.conf import settings


class Amenity(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField()
    stars = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.address})"


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    amenities = models.ManyToManyField(Amenity, blank=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f"Бронь {self.user.username} - {self.room}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    stay_period = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.room}"