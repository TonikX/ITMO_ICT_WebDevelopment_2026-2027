from datetime import date, timedelta
from django.db.models import Sum, Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import ReadingHall, Reader, Book, BookCopy, BookLoan
from .serializers import (
    ReadingHallSerializer, ReaderSerializer, BookSerializer,
    BookCopySerializer, BookLoanSerializer,
    ReaderNestedSerializer, BookDetailSerializer, BookLoanNestedSerializer
)


class ReadingHallViewSet(viewsets.ModelViewSet):
    queryset = ReadingHall.objects.all()
    serializer_class = ReadingHallSerializer

    @action(detail=True, methods=['get'])
    def readers(self, request, pk=None):
        """GET /halls/{id}/readers/"""
        hall = self.get_object()
        return Response(ReaderSerializer(hall.readers.all(), many=True).data)

    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """GET /halls/{id}/books/"""
        hall = self.get_object()
        return Response(BookCopySerializer(hall.copies.all(), many=True).data)


class ReaderViewSet(viewsets.ModelViewSet):
    queryset = Reader.objects.select_related('hall').all()

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReaderNestedSerializer
        return ReaderSerializer

    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """GET /readers/{id}/books/"""
        reader = self.get_object()
        active_loans = reader.loans.filter(returned_at__isnull=True)
        return Response(BookLoanNestedSerializer(active_loans, many=True).data)

    @action(detail=False, methods=['post'])
    def deactivate_old(self, request):
        """POST /readers/deactivate_old/"""
        one_year_ago = date.today() - timedelta(days=365)
        qs = Reader.objects.filter(
            registered_at__lt=one_year_ago,
            re_registered_at__isnull=True,
            is_active=True
        )
        updated = qs.update(is_active=False)
        return Response({'deactivated_count': updated})


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookSerializer


class BookCopyViewSet(viewsets.ModelViewSet):
    queryset = BookCopy.objects.select_related('book', 'hall').all()
    serializer_class = BookCopySerializer


class BookLoanViewSet(viewsets.ModelViewSet):
    queryset = BookLoan.objects.select_related('book', 'reader', 'hall').all()
    serializer_class = BookLoanSerializer



class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def overdue_loans(self, request):
        """GET /analytics/overdue_loans/"""
        threshold = date.today() - timedelta(days=30)
        qs = BookLoan.objects.filter(
            returned_at__isnull=True,
            issued_at__lt=threshold
        ).select_related('reader', 'book')
        return Response(BookLoanNestedSerializer(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def readers_under_20(self, request):
        """GET /analytics/readers_under_20/"""
        threshold = date.today() - timedelta(days=20 * 365)
        count = Reader.objects.filter(birth_date__gt=threshold).count()
        return Response({'readers_under_20': count})

    @action(detail=False, methods=['get'])
    def rare_books_readers(self, request):
        """GET /analytics/rare_books_readers/ """
        rare_book_ids = (
            BookCopy.objects.values('book_id')
            .annotate(total=Sum('quantity'))
            .filter(total__lte=2)
            .values_list('book_id', flat=True)
        )

        readers = Reader.objects.filter(
            loans__book_id__in=rare_book_ids,
            loans__returned_at__isnull=True
        ).distinct()
        return Response(ReaderSerializer(readers, many=True).data)

    @action(detail=False, methods=['get'])
    def education_stats(self, request):
        """GET /analytics/education_stats/"""
        total = Reader.objects.count()
        stats = Reader.objects.values('education').annotate(count=Count('id')).order_by()

        result = []
        for item in stats:
            edu_code = item['education']

            edu_name = dict(Reader.EDUCATION_CHOICES).get(edu_code, edu_code)
            percent = round(item['count'] * 100 / total, 2) if total > 0 else 0.0
            result.append({
                'education': edu_code,
                'education_name': edu_name,
                'count': item['count'],
                'percent': percent
            })
        return Response({'total': total, 'stats': result})

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """GET /analytics/monthly_report/"""
        today = date.today()
        month_start = today.replace(day=1)

        halls = ReadingHall.objects.all()
        halls_data = []

        for hall in halls:
            halls_data.append({
                'hall_number': hall.hall_number,
                'name': hall.name,
                'active_readers': hall.readers.filter(is_active=True).count(),
                'book_positions': hall.copies.count(),
                'new_readers_this_month': hall.readers.filter(registered_at__gte=month_start).count()
            })

        return Response({
            'month': month_start.strftime('%Y-%m'),
            'total_active_readers': Reader.objects.filter(is_active=True).count(),
            'total_books': Book.objects.count(),
            'new_readers_total': Reader.objects.filter(registered_at__gte=month_start).count(),
            'halls': halls_data
        })