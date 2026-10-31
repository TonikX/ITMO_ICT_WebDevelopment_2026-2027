# Страницы и маршруты

Все маршруты приложения сосредоточены в `homework/urls.py`:

```python
app_name = 'homework'

urlpatterns = [
    path('', views.index, name='index'),
    path('homework/<int:pk>/', views.homework_detail, name='homework_detail'),
    path('my/', views.my_submissions, name='my_submissions'),
    path('summary/', views.class_summary, name='class_summary'),
    path('register/', views.register, name='register'),
]
```

В корневом `config/urls.py` дополнительно подключаются админка Django
и стандартные url-ы авторизации (`django.contrib.auth.urls`):

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('homework.urls')),
]
```

## Таблица маршрутов

| URL                          | Имя                   | Вид файла                     | Описание |
|------------------------------|-----------------------|-------------------------------|----------|
| `/`                          | `homework:index`      | `views.index`                 | Список ДЗ: фильтр, поиск, пагинация |
| `/homework/<pk>/`            | `homework_detail`     | `views.homework_detail`       | Страница задания + сдача решения |
| `/my/`                       | `my_submissions`      | `views.my_submissions`        | Сданные работы текущего пользователя |
| `/summary/`                  | `class_summary`       | `views.class_summary`         | Сводка отметок класса |
| `/register/`                 | `register`            | `views.register`              | Регистрация пользователя |
| `/accounts/login/`, `/accounts/logout/` | `login`, `logout` | встроенные Django views | Вход и выход |
| `/admin/...`                 | —                     | Django Admin                  | Панель администратора |

## Что делает каждая страница

### `/` — список заданий
QuerySet всех `Homework`, упорядоченный по сроку сдачи. Поддерживает
GET-параметры `subject` (фильтр по предмету) и `q` (поиск), пагинация по 5
(см. [Пагинация и фильтрация](filters.md)). Для авторизованного ученика
на карточках показывается бейдж "✓ сдано", если решение уже отправлено.

### `/homework/<pk>/` — страница задания
Общая часть — полное описание задания (текст, преподаватель, сроки, штрафы).
Дальше страница раздваивается по роли:

- **ученик** — форма сдачи решения; если решение уже есть — его текст,
  статус отметки, и (пока нет отметки) кнопки "Сохранить изменения"
  и "Удалить решение";
- **учитель** — таблица всех сданных работ с отметками и ссылка на админку.

Обработка POST-действий `submit` / `update` / `delete` происходит в одной вьюхе
`homework_detail` с проверкой прав на каждое действие (см. ниже).

### `/my/` — мои работы
Все `Submission` текущего пользователя (`filter(student=request.user)`)
с отметками, пагинация по 5. Доступ только авторизованным
(декоратор `@login_required`).

### `/summary/` — сводка отметок класса
Строит агрегированный QuerySet:

```python
rows = (base
        .values('homework_id', 'homework__subject')
        .annotate(
            total=Count('id'),
            graded=Count('mark'),
            avg_mark=Avg('mark'),
        )
        .order_by('homework_id'))
```

- **ученик** — подсводка своей группы (`Profile.group`); если группа не указана,
  показываются только его собственные работы;
- **учитель** — выбор произвольной группы через `?group=...` и дополнительная
  таблица "сводка по всем классам".

### `/register/` — регистрация
Форма `UserRegistrationForm` (наследник `UserCreationForm`): логин, пароль
(с валидацией паролей Django) и учебная группа. При сохранении создаётся
`Profile` с группой. Успешная регистрация перенаправляет на страницу входа.

## Контекст в шаблонах

Шаблоны наследуют общий `homework/base.html` (Bootstrap-навигация, алерты
сообщений `{% if messages %}`). Разграничение прав в разметке — см.
[следующий раздел](rights.md).
