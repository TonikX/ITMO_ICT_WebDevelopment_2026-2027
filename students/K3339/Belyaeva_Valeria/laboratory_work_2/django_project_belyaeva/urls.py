from django.contrib import admin
from django.urls import include, path

urlpatterns = [path('admin/', admin.site.urls), path('practice/', include('project_first_app.urls')),
               path('', include('flights.urls'))]
