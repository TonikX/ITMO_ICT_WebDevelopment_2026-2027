from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Табло автогонок: администрирование"
admin.site.site_title = "Табло автогонок"
admin.site.index_title = "Гонки, заезды и результаты"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("races.urls")),
]
