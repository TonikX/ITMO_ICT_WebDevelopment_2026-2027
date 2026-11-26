from django.db.models import F, Q
from django.utils import timezone
from rest_framework import serializers

from . import models


def resource_serializer(model, fields):
    meta = type('Meta', (), {'model': model, 'fields': fields.split()})
    return type(f'{model.__name__}Serializer', (serializers.ModelSerializer,), {'Meta': meta})


AuthorSerializer = resource_serializer(models.Author, 'id_author full_name')
PublisherSerializer = resource_serializer(models.Publisher, 'id_publisher name')
SectionSerializer = resource_serializer(models.Section, 'id_section name')
ReadingRoomSerializer = resource_serializer(models.ReadingRoom, 'id_room room_number name capacity')
BookCopySerializer = resource_serializer(models.BookCopy, 'id_copy book inventory_no acquired_at status')
BookAuthorSerializer = resource_serializer(models.BookAuthor, 'id book author')


class BookSerializer(serializers.ModelSerializer):
    publication_year = serializers.IntegerField(min_value=1400, max_value=2100)
    authors = AuthorSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        source='authors', queryset=models.Author.objects.all(), many=True,
        write_only=True, required=False,
    )

    class Meta:
        model = models.Book
        fields = ('id_book', 'title', 'publisher', 'section', 'publication_year', 'authors', 'author_ids')


class BookDetailSerializer(BookSerializer):
    copies = BookCopySerializer(many=True, read_only=True)

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ('copies',)


class ValidatedSerializer(serializers.ModelSerializer):
    def value(self, attrs, name):
        return attrs.get(name, getattr(self.instance, name, None))

    def other_rows(self):
        rows = self.Meta.model.objects.all()
        return rows.exclude(pk=self.instance.pk) if self.instance else rows


class ReaderSerializer(ValidatedSerializer):
    last_regeq_at = serializers.DateField(required=False)

    class Meta:
        model = models.Reader
        fields = '__all__'

    def validate(self, attrs):
        registered = self.value(attrs, 'registered_at')
        reregistered = self.value(attrs, 'last_regeq_at') or registered
        deregistered = self.value(attrs, 'deregistered_at')
        if self.value(attrs, 'birth_date') > timezone.localdate():
            raise serializers.ValidationError({'birth_date': 'Дата рождения не может быть в будущем.'})
        if not self.value(attrs, 'birth_date') <= registered <= reregistered:
            raise serializers.ValidationError('Даты рождения, регистрации и перерегистрации должны идти по порядку.')
        if deregistered and deregistered < reregistered:
            raise serializers.ValidationError({'deregistered_at': 'Дата снятия с учёта раньше перерегистрации.'})
        return attrs


class HistorySerializer(ValidatedSerializer):
    # История использует полуоткрытые интервалы [valid_from, valid_to).
    def validate(self, attrs):
        owner = self.value(attrs, self.owner_field)
        if self.instance and owner != getattr(self.instance, self.owner_field):
            raise serializers.ValidationError({self.owner_field: 'Нельзя переносить запись истории.'})
        start, end = (self.value(attrs, key) for key in ('valid_from', 'valid_to'))
        if end is not None and end <= start:
            raise serializers.ValidationError({'valid_to': 'Конец должен быть позже начала.'})
        type(owner).objects.select_for_update().get(pk=owner.pk)
        rows = self.other_rows().filter(**{self.owner_field: owner})
        overlap = rows.filter(Q(valid_to__isnull=True) | Q(valid_to__gt=start))
        if end is not None:
            overlap = overlap.filter(valid_from__lt=end)
        if not self.instance:
            # При добавлении более поздней записи модель закроет открытый интервал.
            overlap = overlap.exclude(valid_to__isnull=True, valid_from__lt=start)
        if overlap.exists():
            raise serializers.ValidationError('Период пересекается с другой записью истории.')
        return attrs


class BookCipherHistorySerializer(HistorySerializer):
    owner_field = 'book'

    class Meta:
        model = models.BookCipherHistory
        fields = '__all__'


class CopyRoomHistorySerializer(HistorySerializer):
    owner_field = 'copy'

    class Meta:
        model = models.CopyRoomHistory
        fields = '__all__'


class ReaderTicketHistorySerializer(HistorySerializer):
    owner_field = 'reader'

    class Meta:
        model = models.ReaderTicketHistory
        fields = '__all__'


class ReaderRoomHistorySerializer(HistorySerializer):
    owner_field = 'reader'

    class Meta:
        model = models.ReaderRoomHistory
        fields = '__all__'


class LoanSerializer(ValidatedSerializer):
    class Meta:
        model = models.Loan
        fields = '__all__'

    def validate(self, attrs):
        issue, due, returned = (self.value(attrs, key) for key in ('issued_at', 'due_at', 'returned_at'))
        if due <= issue:
            raise serializers.ValidationError({'due_at': 'Срок возврата должен быть позже выдачи.'})
        if returned is not None and returned < issue:
            raise serializers.ValidationError({'returned_at': 'Возврат не может предшествовать выдаче.'})
        copy = self.value(attrs, 'copy')
        reader = self.value(attrs, 'reader')
        if self.instance and (copy.pk != self.instance.copy_id or reader.pk != self.instance.reader_id):
            raise serializers.ValidationError('Нельзя менять экземпляр или читателя существующей выдачи.')
        copy = models.BookCopy.objects.select_for_update().get(pk=copy.pk)
        if not self.instance and copy.status != models.BookCopy.Status.ACTIVE:
            raise serializers.ValidationError({'copy': 'Экземпляр не находится в фонде.'})
        if not self.instance and reader.deregistered_at is not None and reader.deregistered_at <= issue.date():
            raise serializers.ValidationError({'reader': 'Читатель снят с учёта на дату выдачи.'})
        if issue.date() < max(reader.registered_at, copy.acquired_at):
            raise serializers.ValidationError({'issued_at': 'Выдача раньше регистрации читателя или поступления экземпляра.'})
        if returned == issue:
            return attrs
        overlap = self.other_rows().filter(copy=copy).filter(Q(returned_at__isnull=True) | Q(returned_at__gt=issue))
        overlap = overlap.filter(Q(returned_at__isnull=True) | Q(returned_at__gt=F('issued_at')))
        if returned is not None:
            overlap = overlap.filter(issued_at__lt=returned)
        if overlap.exists():
            raise serializers.ValidationError({'copy': 'Экземпляр уже выдан в этот период.'})
        return attrs
