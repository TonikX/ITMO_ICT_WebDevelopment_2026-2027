from rest_framework import serializers
from .models import (
    Author,
    Publisher,
    Category,
    Book,
    BookCopy,
    Reader,
    ReaderRoom,
    Loan,
    ReaderRoomHistory,
    BookCopyRoomHistory,
)

from .services import register_reader

from django.utils import timezone


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = '__all__'


class ReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = '__all__'
        read_only_fields = ['last_registration_date']


class ReaderRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReaderRoom
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'


class ReaderRoomHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReaderRoomHistory
        fields = '__all__'


class BookCopyRoomHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopyRoomHistory
        fields = '__all__'


class BookDetailSerializer(BookSerializer):
    authors = AuthorSerializer(many=True, read_only=True)


class PublisherDetailSerializer(PublisherSerializer):
    books = BookSerializer(
        source='book_set',
        many=True,
        read_only=True,
    )

    class Meta(PublisherSerializer.Meta):
        fields = ['id', 'name', 'description', 'books']


class ReaderRegistrationSerializer(ReaderSerializer):
    reader_room = serializers.PrimaryKeyRelatedField(
        queryset=ReaderRoom.objects.all(),
        write_only=True
    )

    def create(self, validated_data):
        return register_reader(**validated_data)


class RoomInputSerializer(serializers.Serializer):
    reader_room = serializers.PrimaryKeyRelatedField(
        queryset=ReaderRoom.objects.all()
    )


class ReaderReregisterSerializer(serializers.Serializer):
    library_card_number = serializers.CharField(
        max_length=100,
        required=False
    )


class ReaderUpdateSerializer(ReaderSerializer):
    class Meta(ReaderSerializer.Meta):
        read_only_fields = [
            'last_registration_date',
            'library_card_number'
        ]


class BookCopyAcceptSerializer(RoomInputSerializer):
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all()
    )


class LoanIssueSerializer(serializers.Serializer):
    reader = serializers.PrimaryKeyRelatedField(
        queryset=Reader.objects.all()
    )

    book_copy = serializers.PrimaryKeyRelatedField(
        queryset=BookCopy.objects.all()
    )


class ReaderSummarySerializer(ReaderSerializer):
    class Meta(ReaderSerializer.Meta):
        fields = [
            'id',
            'name',
            'library_card_number'
        ]
        read_only_fields = fields


class MonthlyReportSerializer(serializers.Serializer):
    year = serializers.IntegerField(
        min_value=1,
        max_value=9999
    )

    month = serializers.IntegerField(
        min_value=1,
        max_value=12
    )

    def validate(self, attrs):
        today = timezone.localdate()

        if (attrs['year'], attrs['month']) > (
            today.year, today.month
        ):
            raise serializers.ValidationError(
                "Нельзя сформировать отчёт за будущий месяц"
            )

        return attrs