from django.contrib import admin
from .models import Driver, Race, Registration, Run, Comment
admin.site.register([Driver, Race, Registration, Run, Comment])
