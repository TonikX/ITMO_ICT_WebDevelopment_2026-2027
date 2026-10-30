# Практическое занятие 2 (ЛР2) — «Автовладельцы»

Титор Матвей, группа K3339. Темы: связь «многие ко многим» с собственными
полями, представления (FBV/CBV), формы.

## Задание 1 — связь «многие ко многим» через промежуточную модель

- `Car.owners = ManyToManyField(CarOwner, through='Ownership')`,
- `Ownership` — два внешних ключа (`owner`, `car`) и даты `start_date` / `end_date`
  (дата начала и окончания владения).
- Миграции: `makemigrations` + `migrate`.

## Задание 2 — представления

- **FBV** `get_all_owners` — вывод всех владельцев, шаблон `owners.html`
  (цикл `{% for data in dataset %}`);
- **CBV** для автомобилей: `CarListView` (список, `object_list`),
  `CarDetailView` (один автомобиль, `object`, параметр `<int:pk>`),
  `CarUpdateView` (обновление, форма). Маршруты — через `as_view()`.
- Данные: не менее трёх владельцев и трёх автомобилей (`seed_data`).

## Задание 3 — формы

- **FBV** `create_owner` + `OwnerForm` (ModelForm в `forms.py`):
  GET — форма, POST — `is_valid()` → `form.save()` → `redirect`;
  в шаблоне `{% csrf_token %}` и `{{ form.as_p }}`.
- **CBV** для автомобиля: `CarCreateView`, `CarUpdateView` (поля через `fields`,
  `success_url`), `CarDeleteView` (шаблон подтверждения с POST-формой).
- Ещё не менее трёх владельцев и трёх автомобилей добавляются **через формы**:
  `/owner/create/`, `/cars/create/` (можно воспользоваться `seed_data` + формами).

## Запуск

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data      # 3 владельца, 3 автомобиля, владения
python manage.py runserver      # http://127.0.0.1:8000/
```

## Маршруты

| URL                      | Вид              | Назначение |
|--------------------------|------------------|------------|
| `/owners/`               | FBV              | все владельцы |
| `/owner/<pk>/`           | FBV              | один владелец |
| `/owner/create/`         | FBV + форма      | новый владелец |
| `/cars/`                 | CBV ListView     | все автомобили |
| `/cars/<pk>/`            | CBV DetailView   | один автомобиль |
| `/cars/create/`          | CBV CreateView   | новый автомобиль |
| `/cars/<pk>/update/`     | CBV UpdateView   | изменение автомобиля |
| `/cars/<pk>/delete/`     | CBV DeleteView   | удаление (подтверждение POST) |
