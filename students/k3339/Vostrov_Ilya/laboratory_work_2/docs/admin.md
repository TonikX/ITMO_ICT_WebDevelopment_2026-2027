# Панель администратора

По условию варианта 2 учитель выставляет **оценочную отметку** через
Django-admin. Доступ: `/admin/` (учётная запись с `is_staff`/`is_superuser`,
например `teacher` / `teacher123`).

## Регистрация моделей в `admin.py`

- `Homework` — `HomeworkAdmin` со списком, фильтрами по предмету/преподавателю,
  поиском и быстрым редактированием преподавателя.
- `Submission` — `SubmissionAdmin`: список `задание / ученик / текст / сдано /
  отметка / дата отметки`, фильтр по предмету и отметке, поиск по ученику,
  группе, тексту и предмету.
- Модель `User` расширена `ProfileInline` — поле "Класс / учебная группа"
  доступно прямо в админке пользователя.
- `Profile` зарегистрирована отдельно.

```python
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('homework', 'student', 'short_text', 'submitted_at', 'mark', 'marked_at')
    list_filter = ('homework__subject', 'mark')
    search_fields = ('student__username', 'student__profile__group', 'text', 'homework__subject')
```

## Выставление отметки

1. Учитель заходит в `/admin/homework/submission/`.
2. Открывает нужную работу (или редактирует "галочкой" и выбирает действие).
3. В поле **"Отметка"** вводит балл и сохраняет.

При сохранении `SubmissionAdmin.save_model` автоматически проставляет дату
выставления отметки, если её ещё нет:

```python
def save_model(self, request, obj, form, change):
    """Автоматически проставляем дату выставления отметки."""
    if obj.mark is not None and not obj.marked_at:
        obj.marked_at = timezone.now()
    super().save_model(request, obj, form, change)
```

После этого ученик на странице задания и в "Моих работах" видит отметку
и дату её выставления, а "своё решение" становится только для чтения.
