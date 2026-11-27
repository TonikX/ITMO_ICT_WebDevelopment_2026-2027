from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('authors', AuthorViewSet)
router.register('publishers', PublisherViewSet)
router.register('categories', CategoryViewSet)
router.register('books', BookViewSet)
router.register('book-copies', BookCopyViewSet)
router.register('readers', ReaderViewSet)
router.register('rooms', ReaderRoomViewSet)
router.register('loans', LoanViewSet)
router.register('reader-room-history', ReaderRoomHistoryViewSet)
router.register('book-copy-room-history', BookCopyRoomHistoryViewSet)

router.register(
    'analytics',
    AnalyticsViewSet,
    basename='analytics'
)

router.register(
    'reports',
    ReportViewSet,
    basename='reports'
)

urlpatterns = router.urls