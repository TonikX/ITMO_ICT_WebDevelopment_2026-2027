from datetime import timedelta,date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from tours.models import Country,Agency,Tour,Booking,Review
from project_first_app.models import Car,Ownership,DrivingLicense

class Command(BaseCommand):
    help='Создать вымышленные демонстрационные данные (повторный запуск безопасен).'
    @transaction.atomic
    def handle(self,*args,**options):
        users=[]
        for i in range(1,7):
            user,created=get_user_model().objects.get_or_create(username=f'demo{i}',defaults={
                'first_name':['Анна','Иван','Мария','Олег','Дарья','Павел'][i-1],
                'last_name':'Учебный', 'birth_date':date(1995+i,3,10),
                'passport_number':f'DEMO-{i:04}', 'address':'Учебный город, Примерная улица, 1',
                'nationality':'Не указана'})
            if created:
                user.set_password('Travel-demo-2026!');user.save()
            users.append(user)
        agency,_=Agency.objects.get_or_create(name='Меридиан',defaults={'email':'hello@example.com'})
        destinations=[('Италия','Рим: город историй'),('Грузия','Дорогами Кавказа'),('Турция','Ликийское побережье'),
          ('Россия','Алтай: тишина гор'),('Япония','Сады и огни Киото'),('Марокко','Краски Марракеша'),
          ('Италия','Тосканские каникулы'),('Россия','Карелия: озёра и леса'),('Грузия','Выходные в Тбилиси'),
          ('Турция','Воздушная Каппадокия'),('Япония','Токио за семь дней'),('Марокко','Атлантический маршрут')]
        for i,(country,title) in enumerate(destinations):
            c,_=Country.objects.get_or_create(name=country)
            start=timezone.localdate()+timedelta(days=20+i*7)
            tour,_=Tour.objects.get_or_create(title=title,agency=agency,defaults={'country':c,
              'description':'Неспешное путешествие, местная кухня и прогулки с гидом. В стоимость включены проживание, трансфер и экскурсионная программа. Свободное время для собственных открытий.',
              'start_date':start,'end_date':start+timedelta(days=6),
              'payment_terms':'Предоплата 30% после подтверждения заявки. Остаток — за 7 дней до начала тура. Условия возврата согласовываются с агентством.',
              'price':Decimal(45000+i*7500)})
            Booking.objects.get_or_create(user=users[i%6],tour=tour,defaults={'travelers':i%3+1,
                'unit_price':tour.price,'status':'confirmed' if i%3 else 'pending'})
        past,_=Tour.objects.get_or_create(title='Кавказ: осенние маршруты',agency=agency,defaults={
          'country':Country.objects.get(name='Грузия'),'description':'Завершённый демонстрационный тур с отзывом.',
          'start_date':timezone.localdate()-timedelta(days=20),'end_date':timezone.localdate()-timedelta(days=13),
          'payment_terms':'Оплата по договору.','price':39000})
        Review.objects.get_or_create(user=users[0],tour=past,defaults={'start_date':past.start_date,
          'end_date':past.end_date,'text':'Красивый маршрут и внимательный гид. Особенно понравились прогулки в горах.','rating':9})
        cars=[]
        for i in range(1,8):
            car,_=Car.objects.get_or_create(plate=f'DEMO-{i:03}',defaults={'brand':'Toyota' if i%2 else 'Volvo','model_name':f'Model {i}','color':'Серый'})
            cars.append(car)
        for car in cars[:3]:
            Ownership.objects.get_or_create(owner=users[0],car=car,start_date=date(2020,1,1),defaults={'end_date':date(2021,12,31)})
            Ownership.objects.get_or_create(owner=users[1],car=car,start_date=date(2022,1,1),defaults={'end_date':date(2023,12,31)})
        for i,user in enumerate(users[:2]):
            DrivingLicense.objects.get_or_create(number=f'DEMO00000{i}',defaults={'owner':user,'category':'B','issued_at':date(2019,5,10)})
        self.stdout.write(self.style.SUCCESS('Готово: demo1…demo6 / Travel-demo-2026! Администратора создайте командой createsuperuser.'))
