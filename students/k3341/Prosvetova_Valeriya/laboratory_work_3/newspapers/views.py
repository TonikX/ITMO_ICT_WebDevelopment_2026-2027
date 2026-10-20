from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Delivery, Newspaper, PostOffice, PrintingHouse, PrintRun
from .serializers import (
    DeliverySerializer,
    HousePrintRunSerializer,
    NewspaperHouseSerializer,
    NewspaperSerializer,
    OfficeDeliverySerializer,
    PostOfficeSerializer,
    PrintingHouseSerializer,
    PrintRunSerializer,
)


# --- CRUD + вложенные GET ---

class NewspaperViewSet(viewsets.ModelViewSet):
    queryset = Newspaper.objects.order_by('id')
    serializer_class = NewspaperSerializer

    @action(detail=True, methods=['get'], url_path='printing-houses')
    def printing_houses(self, request, pk=None):
        """№3 (многие-ко-многим): типографии, печатающие газету, с тиражом."""
        newspaper = self.get_object()
        runs = newspaper.print_runs.select_related('printing_house').order_by('printing_house_id')
        return Response(NewspaperHouseSerializer(runs, many=True).data)


class PrintingHouseViewSet(viewsets.ModelViewSet):
    queryset = PrintingHouse.objects.order_by('id')
    serializer_class = PrintingHouseSerializer

    @action(detail=True, methods=['get'], url_path='print-runs')
    def print_runs(self, request, pk=None):
        """№1 (один-ко-многим): тиражи типографии с вложенной газетой."""
        house = self.get_object()
        runs = house.print_runs.select_related('newspaper').order_by('newspaper_id')
        return Response(HousePrintRunSerializer(runs, many=True).data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Закрытие типографии: её тиражи и поставки переходят к другим работающим типографиям."""
        with transaction.atomic():
            house = get_object_or_404(PrintingHouse.objects.select_for_update(), pk=pk)
            if not house.is_active:
                return Response({'detail': 'Типография уже закрыта.'}, status=status.HTTP_409_CONFLICT)
            others = PrintingHouse.objects.filter(is_active=True).exclude(pk=house.pk)
            if not others.exists():
                return Response({'detail': 'Нет других работающих типографий.'}, status=status.HTTP_409_CONFLICT)

            moves = []
            for run in house.print_runs.order_by('newspaper_id'):
                # 1) типография, которая уже печатает эту газету самым большим тиражом
                target_id = (PrintRun.objects.filter(newspaper_id=run.newspaper_id, printing_house__in=others)
                             .order_by('-circulation', 'printing_house_id')
                             .values_list('printing_house_id', flat=True).first())
                # 2) иначе наименее загруженная типография
                if target_id is None:
                    target_id = (others.annotate(total=Coalesce(Sum('print_runs__circulation'), 0))
                                 .order_by('total', 'id').values_list('id', flat=True).first())

                target_run, created = PrintRun.objects.get_or_create(
                    printing_house_id=target_id, newspaper_id=run.newspaper_id,
                    defaults={'circulation': run.circulation})
                if not created:
                    PrintRun.objects.filter(pk=target_run.pk).update(circulation=F('circulation') + run.circulation)
                for d in run.deliveries.all():
                    target_d, created = Delivery.objects.get_or_create(
                        print_run=target_run, post_office_id=d.post_office_id, defaults={'quantity': d.quantity})
                    if not created:
                        Delivery.objects.filter(pk=target_d.pk).update(quantity=F('quantity') + d.quantity)
                run.delete()
                moves.append({'newspaper_id': run.newspaper_id, 'to_printing_house_id': target_id,
                              'circulation': run.circulation})

            house.is_active = False
            house.save(update_fields=['is_active'])
        return Response({'printing_house_id': house.id, 'moves': moves})


class PostOfficeViewSet(viewsets.ModelViewSet):
    queryset = PostOffice.objects.order_by('id')
    serializer_class = PostOfficeSerializer

    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """№2 (один-ко-многим): поставки в отделение с вложенными типографией и газетой."""
        office = self.get_object()
        deliveries = (office.deliveries.select_related('print_run__printing_house', 'print_run__newspaper')
                      .order_by('id'))
        return Response(OfficeDeliverySerializer(deliveries, many=True).data)


class PrintRunViewSet(viewsets.ModelViewSet):
    queryset = PrintRun.objects.order_by('id')
    serializer_class = PrintRunSerializer


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.order_by('id')
    serializer_class = DeliverySerializer


# --- Аналитика ---

def _bad_request(message):
    return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def printing_addresses(request, newspaper_id):
    """Q1. По каким адресам печатается газета?"""
    newspaper = get_object_or_404(Newspaper, pk=newspaper_id)
    houses = (PrintingHouse.objects.filter(print_runs__newspaper=newspaper).distinct().order_by('id')
              .values('name', 'address', printing_house_id=F('id')))
    return Response(list(houses))


@api_view(['GET'])
def top_editor(request, printing_house_id):
    """Q2. Фамилия редактора газеты, которая печатается в типографии самым большим тиражом."""
    house = get_object_or_404(PrintingHouse, pk=printing_house_id)
    run = house.print_runs.select_related('newspaper').order_by('-circulation', 'newspaper_id').first()
    if run is None:
        return Response({'detail': 'В типографии нет тиражей.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({
        'newspaper': {'id': run.newspaper.id, 'title': run.newspaper.title},
        'circulation': run.circulation,
        'editor_last_name': run.newspaper.editor_last_name,
    })


@api_view(['GET'])
def post_offices_by_price(request):
    """Q3. На какие почтовые отделения поступает газета с ценой больше указанной?"""
    try:
        price = Decimal(request.query_params['price_gt'])
    except (KeyError, InvalidOperation):
        return _bad_request('Укажите числовой параметр price_gt.')
    if not price.is_finite():
        return _bad_request('Укажите числовой параметр price_gt.')
    offices = (PostOffice.objects.filter(deliveries__print_run__newspaper__price__gt=price).distinct()
               .order_by('id').values('id', 'number', 'address'))
    return Response(list(offices))


@api_view(['GET'])
def low_deliveries(request):
    """Q4. Какие газеты и куда (номер почты) поступают в количестве меньшем заданного?"""
    try:
        limit = int(request.query_params['quantity_lt'])
    except (KeyError, ValueError):
        return _bad_request('Укажите целочисленный параметр quantity_lt.')
    rows = (Delivery.objects
            .values('print_run__newspaper_id', 'print_run__newspaper__title',
                    'print_run__newspaper__publication_index', 'post_office_id', 'post_office__number')
            .annotate(total=Sum('quantity'))
            .filter(total__lt=limit)
            .order_by('print_run__newspaper_id', 'post_office__number'))
    return Response([{
        'newspaper': {'id': r['print_run__newspaper_id'], 'title': r['print_run__newspaper__title'],
                      'publication_index': r['print_run__newspaper__publication_index']},
        'post_office': {'id': r['post_office_id'], 'number': r['post_office__number']},
        'total_quantity': r['total'],
    } for r in rows])


@api_view(['GET'])
def destinations(request, newspaper_id):
    """Q5. Куда поступает газета, печатающаяся по данному адресу?"""
    newspaper = get_object_or_404(Newspaper, pk=newspaper_id)
    address = request.query_params.get('address')
    if not address:
        return _bad_request('Укажите параметр address.')
    rows = (Delivery.objects.filter(print_run__newspaper=newspaper, print_run__printing_house__address=address)
            .values('post_office_id', 'post_office__number', 'post_office__address')
            .annotate(total=Sum('quantity'))
            .order_by('post_office__number'))
    return Response([{
        'post_office': {'id': r['post_office_id'], 'number': r['post_office__number'],
                        'address': r['post_office__address']},
        'quantity': r['total'],
    } for r in rows])


@api_view(['GET'])
def newspaper_reference(request, newspaper_id):
    """Справка об индексе и цене газеты."""
    newspaper = get_object_or_404(Newspaper, pk=newspaper_id)
    return Response({'id': newspaper.id, 'title': newspaper.title,
                     'publication_index': newspaper.publication_index, 'price': f'{newspaper.price:.2f}'})


@api_view(['GET'])
def printing_houses_report(request):
    """Отчёт о работе типографий с почтовыми отделениями (3 агрегирующих запроса на весь отчёт)."""
    houses = (PrintingHouse.objects.annotate(total_copies=Coalesce(Sum('print_runs__circulation'), 0))
              .order_by('id'))
    report = {h.id: {'id': h.id, 'name': h.name, 'address': h.address, 'is_active': h.is_active,
                     'total_copies': h.total_copies, 'by_newspaper': [], 'shipments': []}
              for h in houses}

    runs = (PrintRun.objects.values('printing_house_id', 'newspaper_id', 'newspaper__title', 'circulation')
            .order_by('printing_house_id', 'newspaper_id'))
    for r in runs:
        report[r['printing_house_id']]['by_newspaper'].append({
            'newspaper': {'id': r['newspaper_id'], 'title': r['newspaper__title']},
            'circulation': r['circulation'],
        })

    shipments = (Delivery.objects
                 .values('print_run__printing_house_id', 'post_office_id', 'post_office__number',
                         'post_office__address', 'print_run__newspaper_id', 'print_run__newspaper__title')
                 .annotate(total=Sum('quantity'))
                 .order_by('print_run__printing_house_id', 'post_office__number', 'print_run__newspaper_id'))
    for s in shipments:
        house_shipments = report[s['print_run__printing_house_id']]['shipments']
        if not house_shipments or house_shipments[-1]['post_office']['id'] != s['post_office_id']:
            house_shipments.append({
                'post_office': {'id': s['post_office_id'], 'number': s['post_office__number'],
                                'address': s['post_office__address']},
                'items': [],
            })
        house_shipments[-1]['items'].append({
            'newspaper': {'id': s['print_run__newspaper_id'], 'title': s['print_run__newspaper__title']},
            'quantity': s['total'],
        })
    return Response(list(report.values()))
