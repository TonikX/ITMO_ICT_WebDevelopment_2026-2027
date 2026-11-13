from project_first_app.models import CarOwner, Car, Ownership, DriverLicense

# все машины марки Toyota
print('1)', list(Car.objects.filter(brand='Toyota')))

# все владельцы по имени Андрей
print('2)', list(CarOwner.objects.filter(first_name='Андрей')))

# случайный владелец -> его id -> его удостоверение
owner = CarOwner.objects.order_by('?').first() # запрос 1
print('3) Владелец:', owner, '- id =', owner.id)
lic = DriverLicense.objects.get(owner_id=owner.id) # запрос 2
print('   Удостоверение:', lic.license_number, '- тип', lic.license_type,
      '- выдано', lic.issue_date)

# все владельцы красных машин
print('4)', list(CarOwner.objects.filter(cars__color='красный').distinct()))

# владельцы, чье владение началось в 2019 году
print('5)', list(CarOwner.objects.filter(ownerships__start_date__year=2019).distinct()))