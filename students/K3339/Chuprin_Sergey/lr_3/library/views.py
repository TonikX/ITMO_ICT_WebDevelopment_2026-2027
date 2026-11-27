from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import *
from .serializers import *

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import mixins
from . import services

from . import analytics

from . import reports


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminUser]


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PublisherDetailSerializer

        return PublisherSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer

        return BookSerializer


class ReaderRoomViewSet(viewsets.ModelViewSet):
    queryset = ReaderRoom.objects.all()
    serializer_class = ReaderRoomSerializer
    permission_classes = [IsAdminUser]


class ReaderViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer
    permission_classes = [IsAdminUser]

    @action(
        detail=False,
        methods=['post'],
        serializer_class=ReaderRegistrationSerializer
    )
    def register(self, request):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        reader = serializer.save()

        return Response(
            ReaderSerializer(reader).data,
            status=status.HTTP_201_CREATED
        )

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ReaderUpdateSerializer

        return super().get_serializer_class()

    @action(detail=True, methods=['post'])
    def unregister(self, request, pk=None):
        reader = self.get_object()
        services.unregister_reader(reader.pk)

        return Response({
            'message': 'Читатель выписан'
        })

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RoomInputSerializer
    )
    def enroll(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reader = services.enroll_reader(
            self.get_object().pk,
            **serializer.validated_data
        )

        return Response(ReaderSerializer(reader).data)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RoomInputSerializer
    )
    def transfer(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        history = services.transfer_reader(
            self.get_object().pk,
            **serializer.validated_data
        )

        return Response(
            ReaderRoomHistorySerializer(history).data
        )

    @action(
        detail=True,
        methods=['post'],
        serializer_class=ReaderReregisterSerializer
    )
    def reregister(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reader = services.reregister_reader(
            self.get_object().pk,
            **serializer.validated_data
        )

        return Response(ReaderSerializer(reader).data)

    @action(
        detail=False,
        methods=['post'],
        url_path='expel-expired'
    )
    def expel_expired(self, request):
        count = services.expel_expired_readers()

        return Response({
            'expelled_count': count
        })


    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        reader = self.get_object()

        books = analytics.get_reader_books(reader)

        return Response(
            BookSerializer(books, many=True).data
        )


class BookCopyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    permission_classes = [IsAdminUser]

    @action(
        detail=False,
        methods=['post'],
        serializer_class=BookCopyAcceptSerializer
    )
    def accept(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book_copy = services.accept_book_copy(
            **serializer.validated_data
        )

        return Response(
            BookCopySerializer(book_copy).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def scrap(self, request, pk=None):
        book_copy = services.scrap_book_copy(
            self.get_object().pk
        )

        return Response(
            BookCopySerializer(book_copy).data
        )

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RoomInputSerializer
    )
    def transfer(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        history = services.transfer_book_copy(
            self.get_object().pk,
            **serializer.validated_data
        )

        return Response(
            BookCopyRoomHistorySerializer(history).data
        )


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAdminUser]

    @action(
        detail=False,
        methods=['post'],
        serializer_class=LoanIssueSerializer
    )
    def issue(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        loan = services.issue_book(
            **serializer.validated_data
        )

        return Response(
            LoanSerializer(loan).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='return'
    )
    def return_book(self, request, pk=None):
        loan = services.return_book(
            self.get_object().pk
        )

        return Response(LoanSerializer(loan).data)


class ReaderRoomHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReaderRoomHistory.objects.all()
    serializer_class = ReaderRoomHistorySerializer
    permission_classes = [IsAdminUser]


class BookCopyRoomHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BookCopyRoomHistory.objects.all()
    serializer_class = BookCopyRoomHistorySerializer
    permission_classes = [IsAdminUser]


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(
        detail=False,
        methods=['get'],
        url_path='overdue-readers'
    )
    def overdue_readers(self, request):
        readers = analytics.get_overdue_readers()

        return Response(
            ReaderSummarySerializer(readers, many=True).data
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='rare-book-readers'
    )
    def rare_book_readers(self, request):
        readers = analytics.get_rare_book_readers()

        return Response(
            ReaderSummarySerializer(readers, many=True).data
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='young-readers'
    )
    def young_readers(self, request):
        return Response({
            'count': analytics.get_young_readers_count()
        })

    @action(detail=False, methods=['get'])
    def education(self, request):
        return Response(
            analytics.get_education_statistics()
        )


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        serializer = MonthlyReportSerializer(
            data=request.query_params
        )

        serializer.is_valid(raise_exception=True)

        report = reports.get_monthly_report(
            **serializer.validated_data
        )

        return Response(report)