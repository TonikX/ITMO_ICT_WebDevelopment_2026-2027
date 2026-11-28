"""
URL configuration for library_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from library import models, serializers, views

router = DefaultRouter()
router.register('books', views.BookViewSet)
router.register('readers', views.ReaderViewSet)
router.register('reports', views.ReportViewSet, basename='report')
for route, model, serializer, staff_only in (
    ('authors', models.Author, serializers.AuthorSerializer, False),
    ('publishers', models.Publisher, serializers.PublisherSerializer, False),
    ('sections', models.Section, serializers.SectionSerializer, False),
    ('reading-rooms', models.ReadingRoom, serializers.ReadingRoomSerializer, False),
    ('book-authors', models.BookAuthor, serializers.BookAuthorSerializer, False),
    ('book-ciphers', models.BookCipherHistory, serializers.BookCipherHistorySerializer, False),
    ('copies', models.BookCopy, serializers.BookCopySerializer, False),
    ('copy-rooms', models.CopyRoomHistory, serializers.CopyRoomHistorySerializer, False),
    ('reader-tickets', models.ReaderTicketHistory, serializers.ReaderTicketHistorySerializer, True),
    ('reader-rooms', models.ReaderRoomHistory, serializers.ReaderRoomHistorySerializer, True),
    ('loans', models.Loan, serializers.LoanSerializer, True),
):
    router.register(route, views.resource_viewset(model, serializer, staff_only))

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-swagger'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
