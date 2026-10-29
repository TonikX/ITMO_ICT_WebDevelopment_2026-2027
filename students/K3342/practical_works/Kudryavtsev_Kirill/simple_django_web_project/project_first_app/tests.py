from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import Car, CarOwner, Ownership


class PracticeTests(TestCase):
    def setUp(self):
        self.staff = CarOwner.objects.create_superuser('admin', 'admin@example.test', 'Staff-pass-123')
        self.car = Car.objects.create(plate='TEST-1', brand='Lada', model='Vesta', color='Белый')

    def test_owner_form_extended_user_and_detail(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('owner_create'), dict(username='anna', first_name='Анна', last_name='Орлова', birth_date='1995-01-01', passport_number='TEST-001', home_address='Учебный адрес', nationality='Учебное значение', password1='Strong-test-83!', password2='Strong-test-83!'))
        self.assertEqual(response.status_code, 302)
        owner = CarOwner.objects.get(username='anna')
        self.assertTrue(owner.check_password('Strong-test-83!'))
        self.assertContains(self.client.get(reverse('owner_detail', args=[owner.pk])), 'TEST-001')
        self.assertContains(self.client.get(reverse('owner_list')), 'Анна')
        self.client.logout()
        self.assertNotContains(self.client.get(reverse('owner_detail', args=[owner.pk])), 'TEST-001')

    def test_car_cbv_create_update_delete(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(reverse('car_create'), dict(plate='TEST-2', brand='Kia', model='Rio', color='Синий')).status_code, 302)
        car = Car.objects.get(plate='TEST-2')
        self.assertContains(self.client.get(reverse('car_list')), 'Kia')
        self.assertEqual(self.client.post(reverse('car_edit', args=[car.pk]), dict(plate='TEST-2', brand='Kia', model='Rio', color='Красный')).status_code, 302)
        self.assertContains(self.client.get(reverse('car_detail', args=[car.pk])), 'Красный')
        self.client.get(reverse('car_delete', args=[car.pk]))
        self.assertTrue(Car.objects.filter(pk=car.pk).exists())
        self.client.post(reverse('car_delete', args=[car.pk]))
        self.assertFalse(Car.objects.filter(pk=car.pk).exists())

    def test_through_ownership_dates_and_license_admin(self):
        Ownership.objects.create(owner=self.staff, car=self.car, start_date=date(2020, 1, 1), end_date=date(2021, 1, 1))
        overlap = Ownership(owner=self.staff, car=self.car, start_date=date(2020, 6, 1))
        with self.assertRaises(ValidationError):
            overlap.full_clean()
        adjacent = Ownership(owner=self.staff, car=self.car, start_date=date(2021, 1, 1))
        adjacent.full_clean()
        adjacent.save()
        self.assertEqual(list(self.car.owners.distinct()), [self.staff])
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('admin:project_first_app_carowner_change', args=[self.staff.pk])).status_code, 200)
