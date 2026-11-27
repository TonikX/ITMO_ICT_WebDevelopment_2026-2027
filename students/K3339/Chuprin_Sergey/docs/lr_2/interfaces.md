# Интерфейсы

### Страницы

| URL | Страница | Доступ |
|-----|----------|--------|
| `/` | Список конференций: поиск, фильтр по тематике и времени, пагинация | Все |
| `/conference/<id>/` | Конференция и отзывы к ней | Все |
| `/conference/<id>/feedback/` | Добавление отзыва | Авторизованные |
| `/conference/<id>/participants/` | Таблица участников конференции | Все |
| `/registrations/` | Мои заявки на выступление | Авторизованные |
| `/registration_create/<id>/` | Подача заявки | Авторизованные |
| `/registration_edit/<id>/` | Редактирование своей заявки | Автор заявки |
| `/registration_delete/<id>/` | Удаление своей заявки | Автор заявки |
| `/registration/<id>/status/` | Смена статуса и результата заявки | Администратор |
| `/feedback/<id>/delete/` | Удаление отзыва | Администратор |
| `/register/`, `/login/`, `/logout/` | Регистрация, вход, выход | Все |

### Разграничение прав

Права проверяются в представлениях (`@login_required`, `request.user.is_staff`)
и в шаблонах (`{% if user.is_staff %}`):

- обычный пользователь видит в таблице участников только принятые заявки;
- администратор видит все заявки, меняет их статус и результат выступления прямо
  в таблице участников, может удалять отзывы и видит ссылку на админ-панель.

### Список конференций: поиск, фильтрация, пагинация

```python
def conference_list(request):
    all_conferences = Conference.objects.order_by('-start_date')

    # Поиск по названию и описанию
    q = request.GET.get('q', '').strip()
    if q:
        all_conferences = all_conferences.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    # Фильтр по тематике
    topic_id = request.GET.get('topic', '')
    if topic_id.isdigit():
        all_conferences = all_conferences.filter(topics__id=topic_id)

    # Фильтр по времени
    period = request.GET.get('period', '')
    now = timezone.now()
    if period == 'upcoming':
        all_conferences = all_conferences.filter(end_date__gte=now)
    elif period == 'past':
        all_conferences = all_conferences.filter(end_date__lt=now)

    paginator = Paginator(all_conferences, 10)
    page_num = request.GET.get('page', 1)
    try:
        # Если существует, то выбираем эту страницу
        current_conferences = paginator.page(page_num)
    except PageNotAnInteger:
        # Если не число
        current_conferences = paginator.page(1)
    except EmptyPage:
        # Если вышли за последнюю страницу, то возвращаем последнюю
        current_conferences = paginator.page(paginator.num_pages)

    # Параметры фильтров для ссылок пагинации (без page)
    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'conference_list.html', {
        'conferences': current_conferences,
        'topics': Topic.objects.order_by('name'),
        'querystring': params.urlencode(),
    })
```

### Смена статуса заявки администратором

```python
@login_required
@require_POST
def registration_update_status(request, registration_id):
    if not request.user.is_staff:
        raise PermissionDenied
    registration = get_object_or_404(Registration, pk=registration_id)

    status = request.POST.get('status')
    if status in Registration.Status.values:
        registration.status = status
        if status != Registration.Status.APPROVED:
            registration.is_recommended = None

    result_values = {'': None, 'true': True, 'false': False}
    result = request.POST.get('result')
    if result in result_values and registration.status == Registration.Status.APPROVED:
        registration.is_recommended = result_values[result]

    registration.save(update_fields=['status', 'is_recommended'])
    return redirect(f'/conference/{registration.conference.id}/participants/')
```

### Запуск

Из папки `lr_2/django_project_chuprin`:

```bash
pip install django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Сайт открывается по адресу `http://127.0.0.1:8000/`, админ-панель — `/admin/`.
