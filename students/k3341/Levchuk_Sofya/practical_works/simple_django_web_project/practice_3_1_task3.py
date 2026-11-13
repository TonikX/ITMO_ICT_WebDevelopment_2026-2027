from django.db.models import Min, Max, Count
from project_first_app.models import CarOwner, Car, Ownership, DriverLicense

# дата выдачи самого старшего водительского удостоверения
print('1)', DriverLicense.objects.aggregate(oldest_license=Min('issue_date')))

# самая поздняя дата владения машиной модели Camry
print('2)', Ownership.objects.filter(car__model_name='Camry')
       .aggregate(latest_start=Max('start_date')))

# количество машин у каждого владельца
for o in CarOwner.objects.annotate(cars_count=Count('cars', distinct=True)):
    print('3)', o, '-', o.cars_count, 'маш.')

# количество машин каждой марки (values = GROUP BY)
for row in Car.objects.values('brand').annotate(cars_count=Count('id')):
    print('4)', row['brand'], '-', row['cars_count'])

# владельцы, отсортированные по дате выдачи удостоверения (+ distinct)
print('5)', list(CarOwner.objects
       .order_by('driver_licenses__issue_date').distinct()))