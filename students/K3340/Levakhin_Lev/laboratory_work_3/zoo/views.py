from django.db import IntegrityError, transaction
from django.db.models import Count, Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from . import models
from . import serializers as schema


# Общтй класс для круд, но добавил транзакции, тчобы избежать ошибок, например если два сотрудника будут параллельно пополнять вольер
class ZooViewSet(viewsets.ModelViewSet):
    def handle_exception(self, exc):
        if isinstance(exc, ProtectedError):
            return Response({"detail": "На запись ссылаются другие данные"}, status=status.HTTP_409_CONFLICT)
        if isinstance(exc, IntegrityError):
            return Response({"detail": "Операция нарушает ограничение базы"}, status=status.HTTP_409_CONFLICT)
        return super().handle_exception(exc)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        get_object_or_404(self.get_queryset().model.objects.select_for_update(), pk=kwargs["pk"])
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        get_object_or_404(self.get_queryset().model.objects.select_for_update(), pk=kwargs["pk"])
        return super().destroy(request, *args, **kwargs)


# Виды, вольеры и сотрудники следяющие за животными
class AnimalViewSet(ZooViewSet):
    serializer_class = schema.AnimalSerializer
    queryset = (models.Animal.objects.select_related("species", "enclosure") # заранее загружаем связанные записи, чтобы потом не обращаться отдельно к базе за каждым видом и вольером
                .prefetch_related("employees").order_by("id")) # загружает сотрудников для всего списка

    @action(detail=True, url_path="building-neighbors")
    def building_neighbors(self, request, pk=None):
        animal = self.get_object()
        building_id = animal.enclosure.building_id if animal.enclosure else None
        neighbors = self.get_queryset().filter(enclosure__building_id=building_id).exclude(pk=animal.pk)
        return Response(self.get_serializer(neighbors if building_id else [], many=True).data)


# Аренда
class LeaseViewSet(ZooViewSet):
    serializer_class = schema.LeaseSerializer
    queryset = models.Lease.objects.select_related("lessor", "lessee").order_by("id")

    def perform_destroy(self, instance):
        if instance.transferred_at:
            raise serializers.ValidationError("Исполненный договор хранится в истории")
        instance.delete()

    def move_animal(self, lease, request, arriving):
        animal = models.Animal.objects.select_for_update().get(pk=lease.animal_id)
        if animal.leases.filter(transferred_at__isnull=False, returned_at__isnull=True).exclude(pk=lease.pk).exists():
            raise serializers.ValidationError("У животного уже есть действующая аренда")
        if arriving:
            field = serializers.IntegerField(min_value=1)
            enclosure_id = field.run_validation(request.data.get("enclosure"))
            enclosure = get_object_or_404(models.Enclosure.objects.select_for_update(), pk=enclosure_id)
            if animal.enclosure_id or enclosure.animals.count() >= enclosure.capacity:
                raise serializers.ValidationError({"enclosure": "Заселение в этот вольер невозможно"})
            animal.enclosure = enclosure
        else:
            if not animal.enclosure_id:
                raise serializers.ValidationError({"enclosure": "У животного нет текущего вольера"})
            animal.enclosure = None
        animal.save(update_fields=["enclosure"])

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def transfer(self, request, pk=None):
        lease = get_object_or_404(models.Lease.objects.select_for_update(), pk=pk)
        if lease.transferred_at:
            raise serializers.ValidationError("Передача уже оформлена")
        if not lease.starts_on <= timezone.localdate() <= lease.ends_on:
            raise serializers.ValidationError("Дата передачи должна входить в срок договора")
        self.move_animal(lease, request, arriving=lease.lessee.is_local)
        lease.transferred_at = timezone.now()
        lease.save(update_fields=["transferred_at"])
        return Response(self.get_serializer(lease).data)

    @action(detail=True, methods=["post"], url_path="return")
    @transaction.atomic
    def return_animal(self, request, pk=None):
        lease = get_object_or_404(models.Lease.objects.select_for_update(), pk=pk)
        if not lease.transferred_at or lease.returned_at:
            raise serializers.ValidationError("Сейчас договор не исполняется")
        self.move_animal(lease, request, arriving=lease.lessor.is_local)
        lease.returned_at = timezone.now()
        lease.save(update_fields=["returned_at"])
        return Response(self.get_serializer(lease).data)


@api_view(["GET"])
def department_counts(request):
    rows = models.Department.objects.values("id", "name").annotate(animal_count=Count("enclosures__animals"))
    return Response(list(rows.order_by("name")))


@api_view(["GET"])
def shared_enclosure_animals(request):
    animals = AnimalViewSet.queryset.filter(enclosure__capacity__gt=1)
    return Response(schema.AnimalSerializer(animals, many=True).data)


@api_view(["GET"])
def empty_enclosures(request):
    enclosures = models.Enclosure.objects.filter(animals__isnull=True).order_by("department_id", "number")
    return Response(schema.EnclosureSerializer(enclosures, many=True).data)


def active_leases():
    return models.Lease.objects.filter(transferred_at__isnull=False, returned_at__isnull=True)


def totals():
    return {"animal_count": Count("animal_id", distinct=True), "total_cost": Sum("total_cost", default=0)}


@api_view(["GET"])
def incoming_leases(request):
    rows = active_leases().filter(lessee__is_local=True).values("lessor_id", "lessor__name")
    return Response(list(rows.annotate(**totals()).order_by("lessor__name", "lessor_id")))


@api_view(["GET"])
def outgoing_report(request):
    leases = active_leases().filter(lessor__is_local=True)
    return Response({
        "by_group": list(leases.values("animal__species__report_group").annotate(**totals()).order_by(
            "animal__species__report_group"
        )),
        "by_zoo": list(leases.values("lessee_id", "lessee__name").annotate(**totals()).order_by(
            "lessee__name", "lessee_id"
        )),
        "total": leases.aggregate(**totals()),
    })
