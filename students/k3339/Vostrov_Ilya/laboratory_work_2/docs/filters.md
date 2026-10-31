# Пагинация и фильтрация

Задание требует пагинацию и фильтрацию/поиск — это реализовано на главной
странице (`/`), а пагинация дополнительно на `/my/`.

## Пагинация

Используется штатный `django.core.paginator.Paginator` (по умолчанию 5 объектов
на страницу, значение берётся из `settings.PAGE_SIZE`):

```python
def _paginate(request, queryset, page_size=None):
    """Разбивает QuerySet на страницы и возвращает объект Page."""
    page_size = page_size or 5
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get('page'))
```

`get_page` корректно обрабатывает несуществующий номер: при `?page=999` вернёт
последнюю страницу, а не ошибку.

В шаблоне пагинация сохраняет активные фильтры — ссылки дополняются текущими
параметрами `subject` и `q`:

```django
{% if pages.has_next %}
  <a href="?page={{ pages.next_page_number }}
            &subject={{ current_subject|urlencode }}
            &q={{ query|urlencode }}">→</a>
{% endif %}
```

## Фильтрация по предмету

Список предметов строится из значений в базе (`distinct().order_by('subject')`),
форма — `<select>` на GET-запрос. Вьюха фильтрует по `subject`:

```python
subject = request.GET.get('subject', '').strip()
if subject:
    queryset = queryset.filter(subject=subject)
```

## Поиск

Поиск по тексту задания **и** преподавателю через `icontains` (регистронезависимо):

```python
query = request.GET.get('q', '').strip()
if query:
    queryset = queryset.filter(Q(text__icontains=query) | Q(teacher__icontains=query))
```

Примеры:

| Запрос                                     | Результат |
|--------------------------------------------|-----------|
| `/?subject=Алгебра`                         | только задания по алгебре |
| `/?q=маятник`                               | задания, в тексте которых есть "маятник" |
| `/?q=Петрова`                               | задания преподавателя Петровой |
| `/?subject=Алгебра&q=интеграл`              | алгебра, где в тексте есть "интеграл" |

## Сводка отметок (агрегация)

Отдельный случай "фильтрации" — сводка класса: QuerySet агрегируется
через `annotate` с `Count` и `Avg` и фильтруется по учебной группе:

```python
rows = (base
        .values('homework_id', 'homework__subject')
        .annotate(
            total=Count('id'),       # сколько сдано
            graded=Count('mark'),    # из них оценено
            avg_mark=Avg('mark'),    # средняя отметка
        )
        .order_by('homework_id'))
```

`Count('mark')` и `Avg('mark')` игнорируют `NULL` — поэтому "оценено"
и "средняя отметка" считаются только по выставленным оценкам.
