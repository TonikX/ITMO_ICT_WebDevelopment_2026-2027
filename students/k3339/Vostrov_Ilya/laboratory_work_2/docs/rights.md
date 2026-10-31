# Разграничение прав

В задании требуется разграничение прав на **клиенте** (в разметке шаблонов)
по флагам `is_staff` / `is_superuser`. В проекте это продублировано и на
стороне сервера — вьюхи проверяют права до принятия решения.

## Роли

| Роль   | Условие                         | Возможности |
|--------|---------------------------------|-------------|
| Аноним  | не авторизован                  | просмотр списка и задания; регистрация/вход |
| Ученик  | авторизован, `is_staff=False`   | сдача/изменение/удаление **своего** решения, свои работы, сводка **своего** класса |
| Учитель | `is_staff=True` или `is_superuser=True` | все работы по заданию, сводка любой группы, отметки через админку |

Вспомогательная функция:

```python
def is_teacher(user):
    """Преподаватель — сотрудник (is_staff) или суперпользователь."""
    return bool(user.is_authenticated and (user.is_staff or user.is_superuser))
```

## На клиенте (шаблоны)

В `homework/base.html` у учителя отображается значок "👨‍🏫 Учитель":

```django
{% if user.is_staff or user.is_superuser %}
  <span class="badge bg-warning text-dark">👨‍🏫 Учитель</span>
{% endif %}
```

В `homework/homework_detail.html` шаблон сам раздваивает содержимое
по роли пользователя:

```django
{% if is_teacher %}
    <!-- таблица всех сданных работ -->
{% else %}
    <!-- форма сдачи / моё решение -->
{% endif %}
```

В `homework/class_summary.html` учителю дополнительно показывается выбор группы
и таблица по всем классам:

```django
{% if is_teacher %}
    <form ...> <select name="group">…</select> …</form>
    …
    <h2>Сводка по всем классам</h2>
{% endif %}
```

В списке заданий (`index.html`) неавторизованному пользователю выводится
подсказка "авторизуйтесь, чтобы сдать".

## На сервере (вьюхи)

Разметка — не защита: вьюхи не полагаются только на неё.

- `my_submissions` — обёрнут `@login_required` (аноним получает редирект на
  `/accounts/login/`).
- `homework_detail` — действия `submit`/`update`/`delete` доступны только
  авторизованному **не-учителю**, причём изменение/удаление — только для своей
  работы и только пока не выставлена отметка (`mark is None`):

```python
if request.method == 'POST' and request.user.is_authenticated:
    action = request.POST.get('action')

    if action == 'submit' and user_submission is None:
        ...
    elif action == 'update' and user_submission and user_submission.mark is None:
        ...
    elif action == 'delete' and user_submission and user_submission.mark is None:
        ...
```

- `class_summary` — учитель выбирает произвольную группу, ученик всегда видит
  только свою (`student__profile__group`); анонимный пользователь не падает,
  а получает пустую сводку:

```python
if not request.user.is_authenticated:
    base = Submission.objects.none()
elif selected:
    base = Submission.objects.filter(student__profile__group=selected)
else:
    base = Submission.objects.filter(student=request.user)
```

- Отметки выставляет **только** учитель — через Django-admin (см.
  [Панель администратора](admin.md)); в формах ученика поля `mark`/`marked_at`
  отсутствуют, поэтому ученик не может их подменить.