import re
from datetime import date
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import serializers as drf_serializers
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS
from rest_framework.response import Response

from . import models, reporting, serializers


class CatalogPermission(BasePermission):
    """ Проверка прав доступа для пользователей """
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and (request.method in SAFE_METHODS or request.user.is_staff))


class ResourceViewSet(viewsets.ModelViewSet):
    """ Расширение класса ModelViewSet
    - проверяем права, используя классы из permission_classes
    - оборачиваем запрос в транзакцию """
    permission_classes = [CatalogPermission]

    def dispatch(self, request, *args, **kwargs):
        # dispatch принимает запрос при обращении к представлению
        if request.method in SAFE_METHODS:
            # если метод 'GET', 'HEAD' или 'OPTIONS', запрос передается далее родительскому классу
            return super().dispatch(request, *args, **kwargs)
        try:
            with transaction.atomic():
                # если метод изменяет данные, то оборачиваем запрос в транзакцию
                return super().dispatch(request, *args, **kwargs)
        except IntegrityError:
            # обрабатываем ошибку при нарушении ограничений бд
            return self.finalize_response(self.request, Response(
            {'detail': 'Операция конфликтует с существующими записями или связями.'}, status=status.HTTP_409_CONFLICT,), *args, **kwargs)


class BookViewSet(ResourceViewSet):
    """ Класс для вывода дополнительной информации о книгах и их экземплярах """
    # queryset - описывает выборку: берет список книг, сортирует по id, ищет для них авторов
    queryset = models.Book.objects.order_by('pk').prefetch_related('authors')
    # сериализатор для списка книг
    serializer_class = serializers.BookSerializer

    def get_queryset(self):
        # action сопоставляет URL и HTTP-метод с методом ViewSet
        queryset = super().get_queryset()
        # выбираем все экземпляры, если задана конкретная книга, иначе - список всех книг
        return queryset.prefetch_related('copies') if self.action == 'retrieve' else queryset

    def get_serializer_class(self):
        # получаем необходимый сериализатор (BookDetailSerializer работает со списком копий)
        return serializers.BookDetailSerializer if self.action == 'retrieve' else self.serializer_class

    @action(detail=True, url_path='copies-by-room')  # detail=True - действие относится к конкретному залу
    def copies_by_room(self, request, pk=None):
        book = self.get_object()
        at = timezone.now()
        # проверям, что экземпляр относится к данной книге, что он есть в фонде и уже размещен
        current = Q(copy_history__copy__book=book, copy_history__copy__status=models.BookCopy.Status.ACTIVE,
                    copy_history__valid_from__lte=at) & (
            Q(copy_history__valid_to__isnull=True) | Q(copy_history__valid_to__gt=at)
        )
        # выбираем уникальные копии из залов по данному условию current, сортируем по ключу
        rows = models.ReadingRoom.objects.annotate(copy_count=Count('copy_history__copy', filter=current, distinct=True,
        )).order_by('pk').values('id_room', 'room_number', 'name', 'copy_count')
        # возвращаем список словарей клиенту
        return Response(list(rows))


def current_loans():
    """ Вспомогательная функция для поиска выдач книг, которые не закрыты возвратом """
    return models.Loan.objects.filter(issued_at__lte=timezone.now(), returned_at__isnull=True).order_by('reader_id', 'pk')


LOAN_REPORT_FIELDS = ('id_loan', 'reader_id', 'reader__full_name', 'copy_id', 'copy__book_id', 'copy__book__title', 'issued_at', 'due_at')

class ReaderViewSet(ResourceViewSet):
    """ Класс для вывода дополнительной информации о читателях """
    permission_classes = [IsAdminUser]  # проверяем флаг is_staff
    queryset = models.Reader.objects.order_by('pk')
    serializer_class = serializers.ReaderSerializer

    @action(detail=True, url_path='current-books')
    def current_books(self, request, pk=None):
        """ Получение книг, которые читатель еще не вернул """
        reader = self.get_object()  # ищем читателя по id из URL
        rows = current_loans().filter(reader=reader)
        #  * - распаковка кортежа для передачи аргументов
        # .values - задает, какие поля попадут в словари
        return Response(list(rows.values(*LOAN_REPORT_FIELDS)))

    @action(detail=False, methods=['post'], url_path='deregister-expired')
    def deregister_expired(self, request):
        """ Исключение из числа действующих читателей тех, кто давно не перерегестрировался"""
        today = timezone.localdate()
        cutoff = reporting.months_before(today, 12)
        # registered_at__lt=cutoff - записался строго раньше даты год назад
        # last_regeq_at__lt=cutoff - последняя перерегистрация (изменение) строго раньше этой даты
        # deregistered_at - ставим сегодняшнюю дату
        updated = (self.queryset.filter(registered_at__lt=cutoff, last_regeq_at__lt=cutoff, deregistered_at__isnull=True,)
                   .update(deregistered_at=today))
        # возвращаем кол-во таких читателей и deregistered_at
        return Response({'deregistered_count': updated, 'deregistered_at': today})


def resource_viewset(model, serializer, staff_only=False):
    return type(f'{model.__name__}ViewSet', (ResourceViewSet,), {
        'queryset': model.objects.order_by('pk'),
        'serializer_class': serializer,
        'permission_classes': [IsAdminUser] if staff_only else [CatalogPermission],
    })



class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, url_path='loans-older-than-month')
    def loans_older_than_month(self, request):
        """ Возвращает список незакрытых выдач, оформленных более месяца назад """
        now = timezone.localtime()
        cutoff = reporting.months_before(now.date(), 1)
        rows = current_loans().filter(issued_at__lt=now.replace(year=cutoff.year, month=cutoff.month, day=cutoff.day))
        return Response(list(rows.values(*LOAN_REPORT_FIELDS)))

    @action(detail=False, url_path='rare-book-loans')
    def rare_book_loans(self, request):
        """ Возвращает незакрытые выдачи книг, у которых не более двух экземпляров в фонде """
        books = models.Book.objects.annotate(copy_count=Count('copies', filter=Q(copies__status=models.BookCopy.Status.ACTIVE),
        )).filter(copy_count__lte=2)  # считаем копии с активным статусом, берем те книги, у которых <= 2 копий
        rows = current_loans().filter(copy__book__in=books)
        return Response(list(rows.values(*LOAN_REPORT_FIELDS)))

    @action(detail=False, url_path='readers-under-20')
    def readers_under_20(self, request):
        """ Возвращает кол-во читателей, младше 20 лет """
        today = timezone.localdate()
        count = reporting.active_readers(today).filter(birth_date__gt=reporting.months_before(today, 240)).count()
        return Response({'reader_count': count})

    @action(detail=False, url_path='reader-demographics')
    def reader_demographics(self, request):
        """ Возвращает число активным читателей; процент читателей, имеющих ученую степень
        и распределение в % читателей по уровню образования"""
        education_counts = {}
        for code in models.Reader.Education.values:
            education_counts[code] = Count('pk', filter=Q(education=code))

        stats = reporting.active_readers(timezone.localdate()).aggregate(total=Count('pk'),
            degree=Count('pk', filter=Q(has_degree=True)),
            **education_counts,)

        total = stats['total']

        def percentage(count):
            return round(count * 100 / total, 2) if total else 0.0

        education_percentage = {}
        for code in education_counts:
            education_percentage[code] = percentage(stats[code])

        return Response({
            'reader_count': total,
            'education_percent': education_percentage,
            'degree_percent': percentage(stats['degree']),
        })


    @action(detail=False, url_path='monthly')
    def monthly(self, request):
        """ Отчет по выбранному месяцу и году """
        raw = request.query_params.get('month', '')
        try:
            if not re.fullmatch(r'[0-9]{4}-[0-9]{2}', raw):
                raise ValueError
            start = date.fromisoformat(f'{raw}-01')
            current_month = timezone.localdate().replace(day=1)
            if start > current_month:
                raise drf_serializers.ValidationError({'month': 'Нельзя построить отчёт за будущий месяц.',})
        except ValueError:
            raise drf_serializers.ValidationError({'month': 'Укажите месяц в формате YYYY-MM.'})
        return Response(reporting.monthly_report(start))

    @action(detail=False, url_path='popular-books')
    def popular_books(self, request):
        """" Возвращает до 10 книг с наибольшим числом выдач за все время """
        rows = models.Book.objects.annotate(loan_count=Count('copies__loans')).filter(loan_count__gt=0)
        return Response(list(rows.order_by('-loan_count', 'pk').values('id_book', 'title', 'loan_count')[:10]))

    @action(detail=False, url_path='stock-by-section')
    def stock_by_section(self, request):
        """ Возвращает число изданий и экземпляров в фонде по каждому разделу """
        rows = models.Section.objects.annotate(
            book_count=Count('books', distinct=True),
            active_copy_count=Count('books__copies', filter=Q(books__copies__status=models.BookCopy.Status.ACTIVE)),
        )
        return Response(list(rows.order_by('pk').values('id_section', 'name', 'book_count', 'active_copy_count')))

    @action(detail=False, url_path='overdue-by-reader')
    def overdue_by_reader(self, request):
        """ Возвращает число невозвращенных просроченных выдач по читателям, фильтруя по убыванию """
        rows = models.Loan.objects.filter(due_at__lt=timezone.now(), returned_at__isnull=True)
        return Response(list(rows.values('reader_id').annotate(overdue_count=Count('pk')).order_by('-overdue_count', 'reader_id')))

    @action(detail=False, url_path='copies-by-room')
    def copies_by_room(self, request):
        # берем дату и время из запроса,raw имеет вид 'ГГГГ-ММ-ДДTЧЧ:ММ:ССZ'
        raw = request.query_params.get('at')
        # если формат неверный или строка пустая, DRF вернет ошибку;
        # если параметр вообще не передали, то выбираем дату и время в данный момент
        at = drf_serializers.DateTimeField().run_validation(raw) if raw is not None else timezone.now()
        active = Q(copy_history__valid_from__lte=at) & ( Q(copy_history__valid_to__isnull=True) | Q(copy_history__valid_to__gt=at))
        rows = models.ReadingRoom.objects.annotate(copy_count=Count('copy_history__copy', filter=active, distinct=True),)
        return Response(list(rows.order_by('pk').values('id_room', 'room_number', 'name', 'copy_count')))
