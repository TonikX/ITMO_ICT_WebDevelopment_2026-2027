from django.contrib import admin
from .models import User, Car, DrivingLicence, Ownership
# Register your models here.

admin.site.register(User)
admin.site.register(Car)
admin.site.register(DrivingLicence)
admin.site.register(Ownership)
