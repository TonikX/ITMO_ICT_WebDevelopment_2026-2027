from django.contrib import admin
from .models import Car, CarOwner, Having, CarLicense

admin.site.register(Car)
admin.site.register(CarOwner)
admin.site.register(Having)
admin.site.register(CarLicense)