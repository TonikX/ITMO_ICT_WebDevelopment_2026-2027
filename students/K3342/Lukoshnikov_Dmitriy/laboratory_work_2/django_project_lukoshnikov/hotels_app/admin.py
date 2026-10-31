from django.contrib import admin
from .models import Hotel, Room, Booking, Amenity, Review

admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Amenity)
admin.site.register(Review)