**Практическое 1:**
меняю имя проекта и имя приложения 

<img width="327" height="517" alt="image" src="https://github.com/user-attachments/assets/77b406c5-a38c-4ab6-b3e7-7512d7e4fcdb" />



Практическое 2.1
Создала модель данных об автовладельцах

<img width="1054" height="292" alt="image" src="https://github.com/user-attachments/assets/6af89264-46e8-4a11-8558-78005d48c589" />

Для организации связей между таблицами использовано поле ForeignKey.


Практическое 2.2 

<img width="718" height="621" alt="image" src="https://github.com/user-attachments/assets/1b35360d-3576-4644-baa4-77dd656ff083" />


Практическое 3
1. Регистрация в админ панели

<img width="702" height="242" alt="image" src="https://github.com/user-attachments/assets/b2b7781f-ba5c-42bb-a68c-213ef34330ab" />

3. создание суперпользователя

<img width="1055" height="209" alt="image" src="https://github.com/user-attachments/assets/941d14b8-8295-4cf3-ae46-6fda24686b0a" />

5. захожу в панель администратора
python manage.py runserver
http://127.0.0.1:8000/admin/

<img width="768" height="537" alt="image" src="https://github.com/user-attachments/assets/4cf4686f-977b-48bc-9f6e-9bf229b139bc" />


Добавила двух владельцев авто

<img width="755" height="453" alt="image" src="https://github.com/user-attachments/assets/f14e2940-5c5a-4cf7-8889-9304db741588" />


Добавила 4 автомобиля

<img width="756" height="449" alt="image" src="https://github.com/user-attachments/assets/bd17903f-158f-4e0f-8319-60c61b3c8c6f" />


Связала каждого владельца минимум с тремя автомобилями так, чтобы не было пересечений по датам владения и продажи.

<img width="775" height="502" alt="image" src="https://github.com/user-attachments/assets/cd62cc02-cad7-4d98-b861-ec8105855861" />


Практическое 4: 
В файле `project_first_app/views.py` было создано представление `owner_detail`, которое получает идентификатор автовладельца и выполняет поиск записи в базе данных с помощью функции `get_object_or_404()`.

<img width="583" height="235" alt="image" src="https://github.com/user-attachments/assets/8b59cb67-487b-480e-b23b-a25ba288e231" />


Практическое 5:

<img width="715" height="373" alt="image" src="https://github.com/user-attachments/assets/39c7261c-ef53-45de-a647-c3987b06e3e9" />

<img width="748" height="250" alt="image" src="https://github.com/user-attachments/assets/ab9ce213-c42f-454f-aadb-29db37439077" />


# Практическое занятие №2.2

Практическое задание 1:
Для организации связи между моделями Automobile и CarOwner используется поле ManyToManyField.
В качестве промежуточной модели указана `Ownership` с помощью параметра through. Модель Ownership содержит два внешних ключа, связывающих автомобиль и автовладельца, а также дополнительные поля позволяющие хранить периоды владения автомобилем.

<img width="558" height="321" alt="image" src="https://github.com/user-attachments/assets/ced5a110-dede-475b-9629-6598ed3ce430" />


Практическое 2:
вывод списка владельцев с помощью FBV
Для реализации вывода всех автовладельцев было создано функциональное представление owner_list в файле views.py. Оно получает все записи модели `CarOwner` с помощью CarOwner.objects.all() и передаёт их в HTML-шаблон owner_list.html

<img width="523" height="198" alt="image" src="https://github.com/user-attachments/assets/0cb8711a-0f9e-4215-a895-1a9dccf9e28a" />


Для вывода всех автомобилей было создано классовое представление AutomobileListView на основе ListView. В представлении указана модель Automobile, HTML-шаблон automobile_list.html и имя контекста automobiles.В шаблоне реализован вывод марки, модели, регистрационного номера и цвета автомобиля. В файле urls.py добавлен маршрут automobiles/, использующий AutomobileListView.as_view().

<img width="476" height="215" alt="image" src="https://github.com/user-attachments/assets/d6fc266a-f90e-4c62-847f-c671611769fd" />


Практическое задание 3
Реализация формы ввода владельца функционально .Для добавления новых автовладельцев была создана форма `CarOwnerForm` на основе класса ModelForm в файле forms.py.
 
<img width="447" height="316" alt="image" src="https://github.com/user-attachments/assets/db4e310b-3196-4c98-808c-ff7ca1d70f46" />


Реализация формы создания, обновления и удаления автомобиля на основе классов. Для создания автомобиля реализовано представление AutomobileCreateView на основе класса CreateView.

<img width="418" height="336" alt="image" src="https://github.com/user-attachments/assets/e78af751-9547-4472-8059-22c64e0d0383" />



Практическое задание
Создание профиля пользователя

Для расширения стандартной модели пользователя Django был выбран способ OneToOneField. Создана модель `UserProfile`, связанная с пользователем через связь «один к одному».

В модели добавлены дополнительные поля:

- `passport_number` — номер паспорта;
    
- `home_address` — домашний адрес;
    
- `nationality` — национальность.
    

Для создания таблицы базы данных была сформирована и применена миграция. Модель `UserProfile` зарегистрирована в Django Admin, что позволяет просматривать и редактировать профили пользователей через административную панель.

<img width="715" height="217" alt="image" src="https://github.com/user-attachments/assets/c544b3b8-0f18-42ff-aa38-00b2ca5cd6c3" />


<img width="721" height="856" alt="image" src="https://github.com/user-attachments/assets/77d2291b-58a2-4bf4-93c9-c53ae5af8693" />


У меня вариант 4
<img width="911" height="274" alt="image" src="https://github.com/user-attachments/assets/3db7f4b4-6058-447f-9ef0-28fda31d903e" />

1.  Создание Django-проекта
Проект создан командой: django-admin startproject travel_agency 
После создания проекта был запущен  сервер

<img width="635" height="588" alt="image" src="https://github.com/user-attachments/assets/36aec08a-a500-420c-a2c9-8a2428137209" />


3. Создание приложения tours
Внутри Django-проекта было создано приложение `tours`, предназначенное для реализации функциональности туристической фирмы.Оно будет отвечать за работу с турами, бронированиями и отзывами пользователей.

4. Созданное приложение `tours` было зарегистрировано в файле travel_agency/settings.py в списке INSTALLED_APPS Это обеспечивает взаимодействие приложения с основным проектом Django и позволяет использовать его модели, представления и административную панель.

<img width="312" height="232" alt="image" src="https://github.com/user-attachments/assets/f5bdbf40-ce2d-47a0-85bf-745affb943ed" />


6. Создание моделей и миграции базы данных
Созданы три модели: `Tour`, `Booking` и `Review`. Модель `Tour` хранит информацию о туристических предложениях, модель `Booking` — данные о бронированиях пользователей и статусах их подтверждения, модель `Review` — отзывы, даты поездки и оценки туристов
7. Применение миграций
Для создания таблиц в базе данных была выполнена команда: python manage.py migrate
Все миграции Django, были применены. Ошибок при создании структуры базы данных не возникло

<img width="798" height="282" alt="image" src="https://github.com/user-attachments/assets/c2261ed1-e18e-4cfc-9d4b-6d47688ce6d4" />


9. Настройка административной панели
В файле  tours/admin.py модели Tour, Booking и Review  были зарегистрированы в Django Admin.
Для управления турами настроены отображение основных полей, фильтрация по стране и турагентству, а также поиск. Для бронирований добавлено административное действие, позволяющее подтвердить выбранные записи и изменить их статус на Подтверждено.
```

from django.contrib import admin  
from .models import Tour, Booking, Review  
  
  
@admin.register(Tour)  
class TourAdmin(admin.ModelAdmin):  
    list_display = ('title', 'agency', 'country', 'start_date', 'end_date', 'price')  
    list_filter = ('country', 'agency')  
    search_fields = ('title', 'country', 'agency')  
  
  
@admin.register(Booking)  
class BookingAdmin(admin.ModelAdmin):  
    list_display = ('user', 'tour', 'booking_date', 'places', 'status')  
    list_filter = ('status', 'booking_date')  
    search_fields = ('user__username', 'tour__title')  
  
    actions = ['confirm_bookings']  
  
    @admin.action(description='Подтвердить выбранные бронирования')  
    def confirm_bookings(self, request, queryset):  
        queryset.update(status=Booking.Status.CONFIRMED)  
  
  
@admin.register(Review)  
class ReviewAdmin(admin.ModelAdmin):  
    list_display = ('tour', 'user', 'rating', 'created_at')  
    list_filter = ('rating', 'created_at')  
    search_fields = ('tour__title', 'user__username')
```

7. Проверка создания тура через административную панель
После настройки Django Admin был добавлен тестовый тур. Тур успешно сохранился и отобразился в списке административной панели.

<img width="929" height="483" alt="image" src="https://github.com/user-attachments/assets/2d171d86-72ee-4a93-a049-2146117d29f0" />


9. Создаю шаблон сайта в templates/tours
10. Создание представления главной страницы
В файле tours/views.py  было создано представление `home`, которое получает список туров из базы данных

11. Настройка маршрутизации и проверка главной страницы
В приложении tours был создан файл urls.py, в котором настроен маршрут главной страницы и связанный с ним обработчик home. Затем маршруты приложения были подключены к основному проекту через функцию include() в файле travel_agency/urls.py

<img width="858" height="907" alt="image" src="https://github.com/user-attachments/assets/5e6749a2-2b05-4076-a7fa-f3dc5d6902fd" />


13. Реализация поиска, фильтрации и пагинации
В каталоге туров реализованы дополнительные возможности работы с данными.
- Поиск туров по названию с использованием `icontains`.
- Фильтрация туров по выбранной стране.
- Пагинация с отображением шести туров на одной странице.
- Сохранение поискового запроса и выбранной страны при переключении страниц.

11. Создание страницы подробной информации о туре
Создан шаблон `tour_detail.html`, отображающий подробную информацию о выбранном туре

<img width="861" height="620" alt="image" src="https://github.com/user-attachments/assets/92574e2f-444c-45d4-b330-c55cc26f883e" />


13.  Создание страницы авторизации

Создан шаблон registration/login.html для входа пользователей в систему. На странице предусмотрены поля для ввода имени пользователя и пароля, кнопка авторизации и отображение сообщения об ошибке при неправильных учётных данных

<img width="687" height="643" alt="image" src="https://github.com/user-attachments/assets/eaffaa5b-c068-43bc-8b7e-f6192ca2f624" />


13. Создание и проверка регистрации
Создана страница регистрации пользователей. Проверена регистрация нового пользователя. После успешного заполнения формы аккаунт создаётся в базе данных, пользователь автоматически входит в систему и перенаправляется на главную страницу сайта.

<img width="382" height="383" alt="image" src="https://github.com/user-attachments/assets/e1ca524e-3209-4a57-8287-ee68e544d6be" />
<img width="769" height="786" alt="image" src="https://github.com/user-attachments/assets/77c0be46-01a2-4de8-a16d-20779e4e5c26" />



15. Настройка и проверка авторизации пользователей
Настроена система авторизации с использованием стандартных средств Django.

Реализованы и проверены следующие функции:
- вход зарегистрированного пользователя;
- выход из аккаунта;
- автоматическое перенаправление на главную страницу после входа;
- автоматическое перенаправление на главную страницу после выхода;
- отображение соответствующих элементов меню для авторизованных и неавторизованных пользователей.

15. Проверка бронирования туров
Проверена работа функции бронирования на сайте. После нажатия кнопки «Забронировать тур» для авторизованного пользователя создаётся заявка со статусом «Ожидает подтверждения». На странице отображается уведомление об успешной отправке заявки.

<img width="755" height="713" alt="image" src="https://github.com/user-attachments/assets/247364d2-f78d-4782-8ef0-b181f661e063" />



17. Страница Мои бронирования
Создана отдельная страница для просмотра бронирований авторизованного пользователя. На странице отображаются название тура, дата бронирования, количество мест и текущий статус заявки. Реализована фильтрация: пользователь видит только собственные бронирования.

<img width="731" height="364" alt="image" src="https://github.com/user-attachments/assets/591f3b32-0302-4636-98b1-c7069175b001" />


19. Редактирование и удаление бронирований
Реализованы функции редактирования и удаления собственных заявок на бронирование. Пользователь может изменять количество мест и удалять заявки, ожидающие подтверждения

<img width="805" height="309" alt="image" src="https://github.com/user-attachments/assets/b9186fe3-6cba-4670-a22a-99e205ddc051" />

<img width="559" height="410" alt="image" src="https://github.com/user-attachments/assets/7c47284a-18a0-4444-9e4c-b6904a794cb3" />



18. Ограничение рейтинга отзывов
В модели `Review` добавлены валидаторы MinValueValidator и MaxValueValidator. Они ограничивают оценку отзыва диапазоном от 1 до 10. Изменения модели сохранены в миграции 0002_alter_review_rating, миграция успешно применена к базе данных.

<img width="880" height="214" alt="image" src="https://github.com/user-attachments/assets/f947d340-84c0-4861-a43a-432acf56c736" />

20. Реализация системы отзывов
Создана форма добавления отзывов с указанием дат поездки, текста комментария и оценки от 1 до 10. Добавлена проверка корректности дат: дата окончания не может быть раньше даты начала. Реализовано сохранение отзывов с привязкой к авторизованному пользователю и выбранному туру. На странице подробной информации о туре добавлен блок отображения отзывов с именем автора, оценкой, датами поездки, текстом и датой публикаци

<img width="508" height="587" alt="image" src="https://github.com/user-attachments/assets/d5ea4eb1-19e7-4000-b618-138a3f289fb6" />


<img width="769" height="317" alt="image" src="https://github.com/user-attachments/assets/84fcd13a-f949-4cae-a9ef-8ae88057e5b2" />

20. Панель управления бронированиями
<img width="846" height="256" alt="image" src="https://github.com/user-attachments/assets/6ec796bf-808b-4421-beed-4d55f3920dbf" />



22. Статистика проданных туров
Создана страница статистики продаж с группировкой подтверждённых бронирований по странам. Для каждой страны рассчитывается общее количество проданных мест.

<img width="741" height="232" alt="image" src="https://github.com/user-attachments/assets/0e92ecae-f3b3-4432-ac76-e94fe6387467" />
