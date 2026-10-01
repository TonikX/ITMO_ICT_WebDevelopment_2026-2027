from django.db.models import Sum
from rest_framework import serializers

from .models import Delivery, Newspaper, PostOffice, PrintingHouse, PrintRun


# --- Обычные сериализаторы для CRUD ---

class NewspaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newspaper
        fields = "__all__"
        read_only_fields = ["printing_houses"]


class PrintingHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintingHouse
        fields = "__all__"
        # закрыть типографию можно только через POST /close/, который переносит её тиражи
        read_only_fields = ["is_active"]


class PostOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostOffice
        fields = "__all__"


class PrintRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintRun
        fields = "__all__"

    def validate(self, attrs):
        house = attrs.get('printing_house')
        if house is not None and not house.is_active:
            raise serializers.ValidationError({'printing_house': 'Типография закрыта.'})
        if self.instance is not None and 'circulation' in attrs:
            delivered = self.instance.deliveries.aggregate(total=Sum('quantity'))['total'] or 0
            if attrs['circulation'] < delivered:
                raise serializers.ValidationError(
                    {'circulation': f'Тираж не может быть меньше уже распределённого ({delivered}).'})
        return attrs


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = "__all__"

    def validate(self, attrs):
        run = attrs.get('print_run') or self.instance.print_run
        quantity = attrs.get('quantity', self.instance.quantity if self.instance else 0)
        others = run.deliveries.all()
        if self.instance is not None:
            others = others.exclude(pk=self.instance.pk)
        delivered = others.aggregate(total=Sum('quantity'))['total'] or 0
        if delivered + quantity > run.circulation:
            raise serializers.ValidationError(
                {'quantity': f'Превышен тираж: доступно {run.circulation - delivered} экз.'})
        return attrs


# --- Вложенные сериализаторы ---

class NewspaperShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newspaper
        fields = ["id", "title", "publication_index", "price"]


class PrintingHouseShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintingHouse
        fields = ["id", "name", "address", "is_active"]


class HousePrintRunSerializer(serializers.ModelSerializer):
    """N1: тиражи типографии с вложенной газетой."""
    newspaper = NewspaperShortSerializer(read_only=True)

    class Meta:
        model = PrintRun
        fields = ["id", "circulation", "newspaper"]


class DeliveryHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintingHouse
        fields = ["id", "name", "address"]


class DeliveryNewspaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newspaper
        fields = ["id", "title", "publication_index"]


class OfficeDeliverySerializer(serializers.ModelSerializer):
    """N2: поставки в почтовое отделение с вложенными типографией и газетой."""
    printing_house = DeliveryHouseSerializer(source='print_run.printing_house', read_only=True)
    newspaper = DeliveryNewspaperSerializer(source='print_run.newspaper', read_only=True)

    class Meta:
        model = Delivery
        fields = ["id", "quantity", "printing_house", "newspaper"]


class NewspaperHouseSerializer(serializers.ModelSerializer):
    """N3: типографии газеты (M2M через PrintRun) с тиражом."""
    printing_house = PrintingHouseShortSerializer(read_only=True)

    class Meta:
        model = PrintRun
        fields = ["printing_house", "circulation"]
