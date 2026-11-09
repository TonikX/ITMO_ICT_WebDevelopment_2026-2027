from django.contrib import admin
from .models import Driver, Car, DriverLisence, DriverCar


admin.site.register([Driver, Car, DriverLisence, DriverCar])

# Register your models here.
