# Реализация

## MVC и Django MVT

В терминологии Django применяется MVT: `Model` — данные, `View` — обработчик запроса,
`Template` — представление. В сопоставлении с MVC обработчик и URL dispatcher выполняют
роль контроллера, а Jinja2-шаблоны — представления.

## Настройка Jinja2

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {'environment': 'config.jinja2.environment'},
    },
    # Стандартный DjangoTemplates оставлен для Django-admin.
]
```

В environment добавлены `url`, `static`, `get_messages` и фильтры `date` и `race_time`.
Пользователь доступен в Jinja2 через `request.user`. Все клиентские шаблоны наследуют
`base.html`, а формы, пагинация и карточки вынесены в `racing/macros.html`.

```jinja
{% if request.user.is_staff or request.user.is_superuser %}
  <a href="{{ url('heat_create', args=[race.slug]) }}">
    Добавить результат
  </a>
{% endif %}
```

## Поиск и пагинация

```python
races = Race.objects.annotate(
    entry_count=Count('entries', distinct=True)
).order_by('start_date', 'pk')
if q:
    races = races.filter(
        Q(title__icontains=q) | Q(track__icontains=q) | Q(location__icontains=q)
    )
if status in dict(Race.STATUSES):
    races = races.filter(status=status)
paginator = Paginator(races, 6)
current_page = paginator.get_page(request.GET.get('page'))
```

Явная сортировка нужна для стабильной пагинации после `annotate()` в Django 3.2.
`get_page()` корректно обрабатывает некорректный номер страницы. Макрос пагинации сохраняет
остальные GET-параметры: запрос, класс, статус и номер страницы комментариев.

Связанные данные протокола получаются через `select_related('entry__driver')`, чтобы не делать
отдельный запрос на каждого гонщика.

## Изменение только своих заявок

```python
entry = get_object_or_404(
    Entry,
    pk=pk,
    race=race,
    driver__user=request.user,
)
```

Идентификатор чужой заявки не даёт доступ к данным: возвращается 404. Сервер дополнительно
проверяет открытие регистрации и отсутствие результатов. Удаление выполняется только POST-запросом
после страницы подтверждения. GET сам по себе данные не изменяет.

## Работа судьи

```python
def staff_only(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied('Доступ только для судей.')
        return view(request, *args, **kwargs)
    return wrapped
```

Декоратор установлен на Race control, создание и изменение результата. Обычный пользователь
получит 403 и при прямом обращении к URL. `HeatForm` ограничивает список заявок текущей гонкой,
поэтому подставить участника другого этапа нельзя.

## Комментарии и валидация

```python
form = CommentForm(request.POST)
form.instance.race, form.instance.author = race, request.user
if form.is_valid():
    form.save()
    return redirect(reverse('race_detail', args=[slug]) + '#discussion')
```

Автор берётся из сессии, а не из отправленного поля. Разрешены типы `cooperation`, `racing`, `other`.
Ошибки рейтинга, дат и пустого текста отображаются возле соответствующего поля.
Jinja2 автоматически экранирует пользовательский текст. Все POST-формы содержат CSRF-токен.
После успешной отправки используется POST/Redirect/GET, предотвращающий повторную отправку
при обновлении страницы.

## Маршруты

| Метод | URL | Действие | Доступ |
|---|---|---|---|
| GET | `/` | Главная, ближайшие гонки, лидеры последней гонки | Все |
| GET | `/races/?q=&status=&page=` | Календарь, поиск и фильтрация | Все |
| GET | `/races/<slug>/?q=&class=&page=&cp=` | Гонка, все заезды, стартовый список, комментарии | Все |
| GET | `/drivers/?q=&class=&page=` | Участники | Все |
| GET, POST | `/account/signup/` | Создание аккаунта | Гость |
| GET, POST | `/account/login/` | Вход | Гость |
| POST | `/account/logout/` | Выход | Все |
| GET | `/account/entries/` | Собственные заявки | Пользователь |
| GET, POST | `/races/<slug>/enter/` | Заявка и профиль гонщика | Пользователь |
| GET, POST | `/races/<slug>/entries/<id>/edit/` | Изменение заявки | Владелец |
| GET, POST | `/entries/<id>/delete/` | Подтверждение / удаление | Владелец |
| POST | `/races/<slug>/comments/` | Комментарий | Пользователь |
| GET | `/control/` | Список гонок для судьи | Staff / superuser |
| GET, POST | `/control/<slug>/heats/new/` | Новый результат | Staff / superuser |
| GET, POST | `/control/<slug>/heats/<id>/` | Правка результата | Staff / superuser |
| GET, POST | `/admin/` | Администрирование | Staff с разрешениями / superuser |

## Анимация

Локальная копия GSAP 3.13.0 используется только для появления первого экрана. Последовательность
задаётся `gsap.timeline()` с перекрытием через position parameter. Изменяются `y` и `autoAlpha`.
`gsap.matchMedia()` исключает анимацию при `prefers-reduced-motion: reduce`; `pagehide` вызывает
`revert()`. Контент изначально видим, поэтому отказ JavaScript не скрывает интерфейс.
