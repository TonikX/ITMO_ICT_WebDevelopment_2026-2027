from django.contrib import admin
from .models import Car, Ownership, DrivingLicense
admin.site.register(Car)
admin.site.register(Ownership)
admin.site.register(DrivingLicense)
