from rest_framework import serializers
from .models import ReadingHall, Reader, Book, BookCopy, BookLoan


class ReadingHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingHall
        fields = '__all__'


class ReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reader
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = '__all__'


class BookLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLoan
        fields = '__all__'



class BookCopyNestedSerializer(serializers.ModelSerializer):
    hall_name = serializers.CharField(source='hall.name', read_only=True)

    class Meta:
        model = BookCopy
        fields = ('id', 'hall', 'hall_name', 'quantity')


class BookLoanNestedSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.__str__', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = BookLoan
        fields = ('id', 'book', 'book_title', 'reader', 'reader_name', 'issued_at', 'returned_at')


class ReaderNestedSerializer(serializers.ModelSerializer):
    hall_name = serializers.CharField(source='hall.name', read_only=True)
    loans = BookLoanNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Reader
        fields = '__all__'


class BookDetailSerializer(serializers.ModelSerializer):
    copies = BookCopyNestedSerializer(many=True, read_only=True)
    loans = BookLoanNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = '__all__'