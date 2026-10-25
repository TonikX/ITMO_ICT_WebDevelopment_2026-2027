
from project_first_app.models import User, Car, Possession, DriverPassport
from django.db.models import Min, Max, Count
# Задание 1. Отображение созданных объектов

print("\nАвтовладельцы:")
owners = User.objects.filter(username__endswith="_lab3")
for owner in owners:
    print(owner.id, owner.first_name, owner.last_name)

print("\nАвтомобили:")
cars = Car.objects.all()
for car in cars:
    print(car.id, car.brand, car.model, car.color)

print("\nВодительские удостоверения:")
passports = DriverPassport.objects.all()
for passport in passports:
    print(passport.owner, passport.passport_number, passport.date_of_issue.date())

print("\nВладения автомобилями:")
possessions = Possession.objects.all()
for possession in possessions:
    print(possession.owner, possession.car)


# Задание 2. Фильтрация данных

# 1. Все автомобили марки Toyota
toyota_cars = Car.objects.filter(brand="Toyota")

print("\nАвтомобили Toyota:")
for car in toyota_cars:
    print(car.brand, car.model)


# 2. Все водители с именем Олег
oleg_drivers = User.objects.filter(first_name="Олег")

print("\nВодители с именем Олег:")
for driver in oleg_drivers:
    print(driver.id, driver.first_name, driver.last_name)


# 3. Получение водительского удостоверения по ID владельца
owner = User.objects.get(username="oleg_lab3")
passport = DriverPassport.objects.get(owner_id=owner.id)

print("\nВодительское удостоверение:")
print(owner.id, owner.first_name, owner.last_name)
print(passport.passport_number, passport.passport_type, passport.date_of_issue.date())


# 4. Владельцы красных автомобилей
red_car_owners = User.objects.filter(possessions__car__color="Красный").distinct()

print("\nВладельцы красных автомобилей:")
for owner in red_car_owners:
    print(owner.id, owner.first_name, owner.last_name)



# 5. Владельцы, начавшие владеть автомобилем в 2024 году
owners_2024 = User.objects.filter(possessions__start_date__year=2024).distinct()

print("\nВладельцы автомобилей с 2024 года:")
for owner in owners_2024:
    print(owner.id, owner.first_name, owner.last_name)



# Задание 3. Агрегация и аннотация

# 1. Дата выдачи самого старого водительского удостоверения
oldest_passport = DriverPassport.objects.aggregate(oldest_date=Min("date_of_issue"))

print("\nДата выдачи самого старого удостоверения:")
print(oldest_passport["oldest_date"].date())



# 2. Самая поздняя дата
latest_ownership = Possession.objects.filter(
    car__model="Camry"
).aggregate(latest_date=Max("start_date"))

print("\nСамая поздняя дата начала владения Toyota Camry:")
print(latest_ownership["latest_date"].date())


# 3. Количество автомобилей у каждого водителя
owners_cars = User.objects.filter(
    username__endswith="_lab3"
).annotate(car_count=Count("possessions__car", distinct=True))

print("\nКоличество автомобилей у каждого водителя:")
for owner in owners_cars:
    print(owner.first_name, owner.last_name, owner.car_count)



# 4. Количество автомобилей каждой марки
cars_by_brand = Car.objects.values("brand").annotate(car_count=Count("id"))

print("\nКоличество автомобилей каждой марки:")
for item in cars_by_brand:
    print(item["brand"], item["car_count"])



# 5. Сортировка владельцев по дате выдачи удостоверения
sorted_owners = User.objects.filter(
    driver_passports__isnull=False
).order_by("driver_passports__date_of_issue").distinct()

print("\nВладельцы по дате выдачи удостоверения:")
for owner in sorted_owners:
    passport = owner.driver_passports.first()
    print(owner.first_name, owner.last_name, passport.date_of_issue.date())
