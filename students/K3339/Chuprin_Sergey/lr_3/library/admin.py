from django.contrib import admin

# Register your models here.

from django.contrib import admin
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

admin.site.register([
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
])