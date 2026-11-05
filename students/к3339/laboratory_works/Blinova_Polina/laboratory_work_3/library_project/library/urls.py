from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReadingHallViewSet, ReaderViewSet, BookViewSet,
    BookCopyViewSet, BookLoanViewSet, AnalyticsViewSet
)

router = DefaultRouter()
router.register(r'halls', ReadingHallViewSet, basename='hall')
router.register(r'readers', ReaderViewSet, basename='reader')
router.register(r'books', BookViewSet, basename='book')
router.register(r'copies', BookCopyViewSet, basename='copy')
router.register(r'loans', BookLoanViewSet, basename='loan')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]