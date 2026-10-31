from django.contrib import admin
from .models import CarOwner, Automobile, Ownership, DriverLicense, UserProfile

admin.site.register(CarOwner)
admin.site.register(Automobile)
admin.site.register(Ownership)
admin.site.register(DriverLicense)
admin.site.register(UserProfile)



