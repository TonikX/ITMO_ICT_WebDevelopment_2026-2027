from datetime import date
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Car, Ownership


class PracticeTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_superuser('admin', password='DemoPass123!')
        self.owner = get_user_model().objects.create_user('owner', first_name='Иван', last_name='Петров',
            passport_number='DEMO-1', home_address='Учебный адрес', nationality='Учебные данные')
        self.car = Car.objects.create(plate_number='DEMO-1', brand='Toyota', model_name='Camry')
        self.client.force_login(self.staff)

    def test_fbv_cbv_forms_and_extended_user(self):
        for path in ['/practice/owners/', f'/practice/owners/{self.owner.pk}/', '/practice/owners/new/',
                     '/practice/cars/', f'/practice/cars/{self.car.pk}/',
                     f'/practice/cars/{self.car.pk}/edit/', '/practice/cars/new/']:
            self.assertEqual(self.client.get(path).status_code, 200)
        response = self.client.post('/practice/owners/new/', {'username': 'new-owner',
            'first_name': 'Мария', 'last_name': 'Иванова', 'email': '', 'birth_date': '1993-01-01',
            'passport_number': 'DEMO-2', 'home_address': 'Тест', 'nationality': 'Тест',
            'password1': 'SafeOwnerPass123!', 'password2': 'SafeOwnerPass123!'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.get(username='new-owner').passport_number, 'DEMO-2')
        self.client.post('/practice/cars/new/', {'plate_number': 'DEMO-2', 'brand': 'Kia', 'model_name': 'Rio', 'color': 'Синий'})
        self.assertTrue(Car.objects.filter(plate_number='DEMO-2').exists())
        self.client.post(f'/practice/cars/{self.car.pk}/edit/', {'plate_number': 'DEMO-1', 'brand': 'Toyota', 'model_name': 'Camry', 'color': 'Белый'})
        self.car.refresh_from_db()
        self.assertEqual(self.car.color, 'Белый')
        self.client.post(f'/practice/cars/{self.car.pk}/delete/')
        self.assertFalse(Car.objects.filter(pk=self.car.pk).exists())

    def test_ownership_intervals_and_access(self):
        Ownership.objects.create(owner=self.owner, car=self.car, start_date=date(2020, 1, 1), end_date=date(2022, 1, 1))
        with self.assertRaises(ValidationError):
            Ownership.objects.create(owner=self.staff, car=self.car, start_date=date(2021, 1, 1))
        Ownership.objects.create(owner=self.staff, car=self.car, start_date=date(2022, 1, 1))
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get('/practice/owners/').status_code, 403)
        self.assertEqual(self.client.get('/practice/cars/').status_code, 403)
