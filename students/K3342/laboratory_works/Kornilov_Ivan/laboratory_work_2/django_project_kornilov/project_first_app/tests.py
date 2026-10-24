from django.test import Client, TestCase

from .models import Car, CarOwner


class CarOwnerViewsTests(TestCase):
    def test_owner_create_and_detail(self):
        client = Client()
        response = client.post('/owners/create/', {
            'username': 'newowner',
            'password': 'Night-river-42',
            'first_name': 'Никита',
            'last_name': 'Орлов',
            'birth_date': '2000-01-02',
            'passport_number': '4011123456',
            'address': 'Невский 1',
            'nationality': 'российская',
        })
        owner = CarOwner.objects.get(username='newowner')
        self.assertRedirects(response, f'/owner/{owner.pk}/')
        self.assertTrue(owner.check_password('Night-river-42'))
        self.assertEqual(owner.passport_number, '4011123456')
        detail = client.get(f'/owner/{owner.pk}/')
        self.assertContains(detail, '4011123456')
        self.assertContains(detail, 'Невский 1')
        listing = client.get('/owners/')
        self.assertContains(listing, 'Орлов')

    def test_car_create_update_delete(self):
        client = Client()
        response = client.post('/cars/create/', {
            'license_plate': 'А000АА178',
            'brand': 'Lada',
            'model_name': 'Granta',
            'color': 'белый',
        })
        car = Car.objects.get(license_plate='А000АА178')
        self.assertRedirects(response, '/cars/')
        detail = client.get(f'/cars/{car.pk}/')
        self.assertContains(detail, 'Granta')
        client.post(f'/cars/{car.pk}/update/', {
            'license_plate': 'А000АА178',
            'brand': 'Lada',
            'model_name': 'Vesta',
            'color': 'белый',
        })
        car.refresh_from_db()
        self.assertEqual(car.model_name, 'Vesta')
        client.post(f'/cars/{car.pk}/delete/')
        self.assertFalse(Car.objects.filter(pk=car.pk).exists())
