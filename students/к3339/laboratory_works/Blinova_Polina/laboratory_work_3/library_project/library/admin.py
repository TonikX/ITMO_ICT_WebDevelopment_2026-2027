from django.contrib import admin
from .models import ReadingHall, Reader, Book, BookCopy, BookLoan


@admin.register(ReadingHall)
class ReadingHallAdmin(admin.ModelAdmin):
    list_display = ('id', 'hall_number', 'name', 'capacity')


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_number', 'last_name', 'first_name', 'hall', 'is_active')
    list_filter = ('hall', 'education', 'is_active')
    search_fields = ('last_name', 'first_name', 'ticket_number')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'authors', 'year', 'section', 'cipher')
    search_fields = ('title', 'authors', 'cipher')


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'hall', 'quantity')
    list_filter = ('hall',)


@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'reader', 'issued_at', 'returned_at')
    list_filter = ('issued_at',)