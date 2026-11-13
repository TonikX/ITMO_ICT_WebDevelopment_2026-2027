from datetime import timedelta,date
from decimal import Decimal
from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.contrib.admin.sites import site
from .models import Country,Agency,Tour,Booking,Review
from project_first_app.models import Car,Ownership

class WorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        U=get_user_model()
        cls.user=U.objects.create_user('alice',password='Strong-pass-2026!')
        cls.other=U.objects.create_user('bob',password='Strong-pass-2026!')
        cls.staff=U.objects.create_superuser('admin',password='Strong-pass-2026!',email='a@example.com')
        cls.country=Country.objects.create(name='Италия')
        cls.agency=Agency.objects.create(name='Агентство')
        cls.tour=Tour.objects.create(title='Рим',country=cls.country,agency=cls.agency,description='Описание',
            start_date=timezone.localdate()+timedelta(days=30),end_date=timezone.localdate()+timedelta(days=37),
            payment_terms='Предоплата',price=Decimal('10000'))
    def login(self,user=None): self.client.force_login(user or self.user)
    def booking(self,status='pending'):
        return Booking.objects.create(user=self.user,tour=self.tour,unit_price=self.tour.price,status=status)
    def test_public_pages_and_jinja(self):
        for path in ['/',reverse('tour_detail',args=[self.tour.pk]),reverse('login'),reverse('register')]:
            self.assertEqual(self.client.get(path).status_code,200)
        self.assertContains(self.client.get('/'),'Коллекция путешествий')
    def test_registration_custom_fields_and_no_privilege_escalation(self):
        r=self.client.post(reverse('register'),{'username':'newuser','password1':'Example-strong-2026!',
            'password2':'Example-strong-2026!','passport_number':'DEMO-123','address':'Пример','nationality':'Тест',
            'is_staff':'on','is_superuser':'on'})
        self.assertEqual(r.status_code,302)
        u=get_user_model().objects.get(username='newuser')
        self.assertEqual(u.passport_number,'DEMO-123');self.assertFalse(u.is_staff);self.assertFalse(u.is_superuser)
        self.assertTrue(u.check_password('Example-strong-2026!'))
    def test_book_login_and_status_price_tampering(self):
        path=reverse('book',args=[self.tour.pk])
        self.assertEqual(self.client.get(path).status_code,302)
        self.login()
        self.assertEqual(self.client.post(path,{'travelers':2,'status':'confirmed','unit_price':1,'user':self.other.pk}).status_code,302)
        b=Booking.objects.get();self.assertEqual(b.user,self.user);self.assertEqual(b.status,'pending')
        self.assertEqual(b.total,20000)
    def test_duplicate_booking(self):
        self.booking();self.login()
        self.client.post(reverse('book',args=[self.tour.pk]),{'travelers':3})
        self.assertEqual(Booking.objects.count(),1)
    def test_invalid_travelers(self):
        self.login()
        for count in [0,21,-1]:
            self.assertEqual(self.client.post(reverse('book',args=[self.tour.pk]),{'travelers':count}).status_code,200)
        self.assertFalse(Booking.objects.exists())
    def test_ownership_protection(self):
        b=self.booking();self.login(self.other)
        for route in ['booking_edit','booking_delete']:
            path=reverse(route,args=[b.pk])
            self.assertEqual(self.client.get(path).status_code,404)
            self.assertEqual(self.client.post(path,{'travelers':3}).status_code,404)
        self.assertTrue(Booking.objects.filter(pk=b.pk).exists())
    def test_edit_resets_confirmation_and_preserves_price(self):
        b=self.booking('confirmed');self.login()
        self.tour.price=20000;self.tour.save()
        self.client.post(reverse('booking_edit',args=[b.pk]),{'travelers':3,'comment':'Ок'})
        b.refresh_from_db();self.assertEqual(b.status,'pending');self.assertEqual(b.total,30000)
    def test_delete_only_on_post(self):
        b=self.booking();self.login();path=reverse('booking_delete',args=[b.pk])
        self.assertEqual(self.client.get(path).status_code,200);self.assertTrue(Booking.objects.exists())
        self.assertEqual(self.client.post(path).status_code,302);self.assertFalse(Booking.objects.exists())
    def test_staff_routes_and_navigation(self):
        self.login()
        for route in ['staff_bookings','sales','tour_create','owners','cars','owner_create']:
            self.assertEqual(self.client.get(reverse(route)).status_code,403)
        self.assertNotContains(self.client.get('/'),'href="/manage/sales/"')
        self.login(self.staff)
        for route in ['staff_bookings','sales','tour_create','owners','cars','owner_create']:
            self.assertEqual(self.client.get(reverse(route)).status_code,200)
        self.assertContains(self.client.get('/'),'href="/manage/sales/"')
    def test_confirmation_post_and_staff_only(self):
        b=self.booking();path=reverse('booking_confirm',args=[b.pk]);self.login()
        self.assertEqual(self.client.post(path).status_code,403)
        self.login(self.staff)
        self.assertEqual(self.client.get(path).status_code,405)
        self.assertEqual(self.client.post(path).status_code,302)
        b.refresh_from_db();self.assertEqual(b.status,'confirmed')
    def test_admin_action(self):
        b=self.booking();self.login(self.staff)
        response=self.client.post(reverse('admin:tours_booking_changelist'),{
            'action':'confirm_selected','_selected_action':[b.pk]})
        self.assertEqual(response.status_code,302)
        b.refresh_from_db();self.assertEqual(b.status,'confirmed')
    def test_sales_aggregate_excludes_pending(self):
        self.booking('confirmed')
        Booking.objects.create(user=self.other,tour=self.tour,unit_price=10000,travelers=4)
        self.login(self.staff);r=self.client.get(reverse('sales'))
        self.assertContains(r,'10000.00 ₽',count=2)
        self.assertNotContains(r,'50000.00 ₽')
    def test_review_snapshot_escape_rating_and_duplicate(self):
        self.login();path=reverse('review_create',args=[self.tour.pk])
        self.client.post(path,{'rating':11,'text':'Тест'});self.assertEqual(Review.objects.count(),0)
        self.client.post(path,{'rating':9,'text':'<script>alert(1)</script>','user':self.other.pk,'start_date':'1990-01-01'})
        rev=Review.objects.get();self.assertEqual(rev.user,self.user);self.assertEqual(rev.start_date,self.tour.start_date)
        r=self.client.get(reverse('tour_detail',args=[self.tour.pk]))
        self.assertContains(r,'&lt;script&gt;');self.assertNotContains(r,'<script>alert')
        self.client.post(path,{'rating':5,'text':'Повтор'});self.assertEqual(Review.objects.count(),1)
    def test_catalog_filters_pagination(self):
        for i in range(8):
            Tour.objects.create(title=f'Рим {i}',country=self.country,agency=self.agency,description='Тест',
                start_date=self.tour.start_date,end_date=self.tour.end_date,payment_terms='Оплата',price=100+i)
        r=self.client.get('/',{'q':'Рим','country':self.country.pk,'max_price':200,'page':2})
        self.assertEqual(r.status_code,200);self.assertContains(r,'class="card"',count=2)
        self.assertContains(r,'q=%D0%A0%D0%B8%D0%BC');self.assertContains(r,'Найдено туров: 8')
    def test_invalid_filter_safe(self):
        for query in [{'country':'oops'},{'max_price':'oops'},{'date_from':'oops'},{'sort':'password'},{'date_from':'2030-01-02','date_to':'2030-01-01'}]:
            self.assertEqual(self.client.get('/',query).status_code,200)
    def test_past_tour_not_bookable(self):
        self.tour.start_date=timezone.localdate()-timedelta(days=1);self.tour.save();self.login()
        self.client.post(reverse('book',args=[self.tour.pk]),{'travelers':1})
        self.assertEqual(Booking.objects.count(),0)
    def test_hidden_tour_not_public(self):
        self.tour.is_active=False;self.tour.save()
        self.assertEqual(self.client.get(reverse('tour_detail',args=[self.tour.pk])).status_code,404)
        self.login(self.staff);self.assertEqual(self.client.get(reverse('tour_detail',args=[self.tour.pk])).status_code,200)
    def test_csrf_and_logout_post(self):
        c=Client(enforce_csrf_checks=True);c.force_login(self.user)
        self.assertEqual(c.post(reverse('book',args=[self.tour.pk]),{'travelers':1}).status_code,403)
        self.assertEqual(c.get(reverse('logout')).status_code,405)
    def test_tour_invalid_dates(self):
        self.tour.end_date=self.tour.start_date-timedelta(days=1)
        with self.assertRaises(ValidationError): self.tour.full_clean()
    def test_practice_owner_fbv_and_car_cbv(self):
        self.login(self.staff)
        # Три владельца и три автомобиля действительно создаются через формы.
        for i in range(3):
            self.assertEqual(self.client.post(reverse('owner_create'),{'username':f'formowner{i}',
              'password1':'Example-strong-2026!','password2':'Example-strong-2026!',
              'passport_number':f'DEMO-{i}','nationality':'Тест','address':'Адрес'}).status_code,302)
            self.assertEqual(self.client.post(reverse('car_create'),{'plate':f'TEST{i}','brand':'Volvo','model_name':'S60','color':'Синий'}).status_code,302)
        car=Car.objects.first()
        self.assertEqual(self.client.get(reverse('car_detail',args=[car.pk])).status_code,200)
        self.client.post(reverse('car_edit',args=[car.pk]),{'plate':car.plate,'brand':'Toyota','model_name':'Corolla','color':'Белый'})
        car.refresh_from_db();self.assertEqual(car.brand,'Toyota')
        self.client.post(reverse('car_delete',args=[car.pk]));self.assertFalse(Car.objects.filter(pk=car.pk).exists())
        self.assertEqual(self.client.get(reverse('owner_detail',args=[self.user.pk])).status_code,200)
    def test_ownership_overlap(self):
        car=Car.objects.create(plate='TEST',brand='A',model_name='B')
        Ownership.objects.create(owner=self.user,car=car,start_date=date(2020,1,1),end_date=date(2021,1,1))
        o=Ownership(owner=self.other,car=car,start_date=date(2020,5,1))
        with self.assertRaises(ValidationError):o.full_clean()
        o.start_date=date(2021,1,2);o.full_clean()
    def test_admin_models_registered(self):
        from project_first_app.models import DrivingLicense
        for model in [get_user_model(),Country,Agency,Tour,Booking,Review,Car,Ownership,DrivingLicense]:
            self.assertIn(model,site._registry)
    def test_login_with_credentials(self):
        self.assertTrue(self.client.login(username='alice',password='Strong-pass-2026!'))
