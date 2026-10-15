from django.contrib import admin

# Register your models here.
from .models import Conference, Registration, Feedback, Topic

admin.site.register(Conference)
admin.site.register(Registration)
admin.site.register(Feedback)
admin.site.register(Topic)
