import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warriors_project.settings')
django.setup()

from warriors_app.models import CarOwner, Car, DriverLicense, Ownership


def run():
    print('1. Машины марки Toyota:')
    for car in Car.objects.filter(brand='Toyota'):
        print(car)
    print()

    print('2. Водители с именем Олег:')
    for owner in CarOwner.objects.filter(first_name='Олег'):
        print(owner)
    print()

    owner = CarOwner.objects.first()
    print(f'3. Удостоверение владельца id={owner.id}:')
    license_obj = DriverLicense.objects.get(owner_id=owner.id)
    print(license_obj)
    print()

    print('4. Владельцы красных машин:')
    for owner in CarOwner.objects.filter(ownerships__car__color='красный').distinct():
        print(owner)
    print()

    print('5. Владельцы, у которых владение началось в 2010:')
    for owner in CarOwner.objects.filter(ownerships__start_date__year=2010).distinct():
        print(owner)
    print()


if __name__ == '__main__':
    run()