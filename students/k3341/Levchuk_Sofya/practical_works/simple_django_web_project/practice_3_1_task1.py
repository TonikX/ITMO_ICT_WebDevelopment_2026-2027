from datetime import date
from project_first_app.models import CarOwner, Car, Ownership, DriverLicense


ivanov = CarOwner.objects.create(username='ivanov_p31', first_name='Иван', last_name='Иванов', birth_date=date(1985, 5, 12))
petrov = CarOwner.objects.create(username='petrov_p31', first_name='Петр', last_name='Петров', birth_date=date(1990, 8, 25))
sergeev = CarOwner.objects.create(username='sergeev_p31', first_name='Сергей', last_name='Сергеев', birth_date=date(1978, 3, 10))
alekseev = CarOwner.objects.create(username='alekseev_p31', first_name='Алексей', last_name='Алексеев', birth_date=date(1982, 11, 5))
andreev = CarOwner.objects.create(username='andreev_p31', first_name='Андрей', last_name='Андреев', birth_date=date(1995, 7, 20))
vasilyev = CarOwner.objects.create(username='vasilyev_p31', first_name='Василий', last_name='Васильев', birth_date=date(1988, 1, 15))

granta = Car.objects.create(plate_number='A111AA02', brand='LADA', model_name='Granta', color='белый')
camry = Car.objects.create(plate_number='T222TT102', brand='Toyota', model_name='Camry', color='красный')
rio = Car.objects.create(plate_number='K333K02', brand='Kia', model_name='Rio', color='серебристый')
x5 = Car.objects.create(plate_number='B444BB702', brand='BMW', model_name='X5', color='черный')
vesta = Car.objects.create(plate_number='H222HH02', brand='LADA', model_name='Vesta', color='синий')
niva = Car.objects.create(plate_number='C666CC102', brand='Chevrolet', model_name='Niva', color='зеленый')
outlander = Car.objects.create(plate_number='M777MM702', brand='Mitsubishi', model_name='Outlander', color='серый')

DriverLicense.objects.create(owner=ivanov, license_number='111111', license_type='B', issue_date=date(2010, 4, 12))
DriverLicense.objects.create(owner=petrov, license_number='222222', license_type='B', issue_date=date(2015, 8, 1))
DriverLicense.objects.create(owner=sergeev, license_number='333333', license_type='C', issue_date=date(2018, 3, 15))
DriverLicense.objects.create(owner=alekseev, license_number='444444', license_type='B', issue_date=date(2012, 11, 20))
DriverLicense.objects.create(owner=andreev, license_number='555555', license_type='A', issue_date=date(2005, 6, 30))
DriverLicense.objects.create(owner=vasilyev, license_number='666666', license_type='B', issue_date=date(2020, 1, 10))

Ownership.objects.create(owner=ivanov, car=granta, start_date=date(2015, 5, 1))
Ownership.objects.create(owner=ivanov, car=camry, start_date=date(2021, 5, 14))
Ownership.objects.create(owner=ivanov, car=rio, start_date=date(2019, 6, 6), end_date=date(2020, 5, 5))

Ownership.objects.create(owner=petrov, car=x5, start_date=date(2021, 8, 18))
Ownership.objects.create(owner=petrov, car=camry, start_date=date(2023, 3, 23), end_date=date(2024, 3, 23))
Ownership.objects.create(owner=petrov, car=rio, start_date=date(2022, 11, 11), end_date=date(2022, 12, 12))

Ownership.objects.create(owner=sergeev, car=vesta, start_date=date(2016, 3, 10))
Ownership.objects.create(owner=sergeev, car=niva, start_date=date(2014, 9, 1))
Ownership.objects.create(owner=sergeev, car=outlander, start_date=date(2017, 12, 5))

Ownership.objects.create(owner=alekseev, car=niva, start_date=date(2013, 4, 1))

Ownership.objects.create(owner=andreev, car=outlander, start_date=date(2019, 12, 1))

Ownership.objects.create(owner=vasilyev, car=camry, start_date=date(2021, 5, 15))

print('Владельцев:', CarOwner.objects.count())
print('Машин:', Car.objects.count())
print('Удостоверений:', DriverLicense.objects.count())
print('Владений:', Ownership.objects.count())

print(list(CarOwner.objects.all()))
print(list(Car.objects.all()))
print(list(Ownership.objects.all()))