from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tours.models import Agency, Country, Tour


class Command(BaseCommand):
    help = "Добавить примеры туров для проверки сайта"

    @transaction.atomic
    def handle(self, *args, **options):
        agency, _ = Agency.objects.get_or_create(
            name="В путь",
            defaults={"phone": "+7 (812) 555-01-20", "email": "info@example.com"},
        )
        examples = [
            ("Выходные в Стамбуле", "Турция", 4, 42000,
             "Прогулки по старому городу, поездка по Босфору и свободный день для знакомства со Стамбулом. В стоимость входят отель, завтраки и трансфер."),
            ("Неделя у моря в Анталье", "Турция", 7, 78000,
             "Отдых в отеле недалеко от пляжа. Проживание, питание и трансфер из аэропорта включены в стоимость. Экскурсии оплачиваются отдельно."),
            ("Тбилиси и Кахетия", "Грузия", 6, 56000,
             "Знакомство с Тбилиси, поездка в Мцхету и два дня в Кахетии. Небольшая группа, проживание в гостевых домах и сопровождение гида."),
            ("Ереван и горные монастыри", "Армения", 5, 49000,
             "Прогулка по Еревану, поездки к озеру Севан, в Гарни и Гегард. В стоимость включены проживание, завтраки и экскурсионная программа."),
            ("Самарканд и Бухара", "Узбекистан", 7, 64000,
             "Маршрут по древним городам с местным гидом. Между городами едем на поезде. Включены отели, завтраки, билеты на поезд и экскурсии."),
            ("Знакомство с Алтаем", "Россия", 8, 71000,
             "Путешествие по Чуйскому тракту с остановками у горных озёр. Ночёвки на турбазах, переезды и сопровождение инструктора входят в стоимость."),
            ("Карелия на выходные", "Россия", 3, 24000,
             "Небольшая поездка из Петербурга: Сортавала, водопады и горный парк Рускеала. Включены автобус, гостиница и завтраки."),
            ("Море и горы Черногории", "Черногория", 9, 96000,
             "Несколько дней на побережье и поездка в национальный парк Дурмитор. В стоимость включены проживание и трансферы по маршруту."),
        ]
        created = 0
        for index, (title, country_name, days, price, description) in enumerate(examples):
            country, _ = Country.objects.get_or_create(name=country_name)
            start = timezone.localdate() + timedelta(days=30 + index * 7)
            _, added = Tour.objects.get_or_create(
                title=title, agency=agency,
                defaults={
                    "country": country, "description": description, "price": price,
                    "start_date": start, "end_date": start + timedelta(days=days - 1),
                    "payment_terms": "Предоплата 30% после подтверждения бронирования. Остаток — за 7 дней до начала тура. Перелёт оплачивается отдельно.",
                },
            )
            created += added
        self.stdout.write(self.style.SUCCESS(f"Добавлено туров: {created}."))
