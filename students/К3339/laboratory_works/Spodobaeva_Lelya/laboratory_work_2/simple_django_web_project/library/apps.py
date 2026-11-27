from django.apps import AppConfig
from django.db.backends.signals import connection_created


def register_search_casefold(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        connection.connection.create_function("tour_casefold", 1, str.casefold, deterministic=True)


class LibraryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "library"
    verbose_name = "Туры туристической фирмы"

    def ready(self):
        connection_created.connect(register_search_casefold)
