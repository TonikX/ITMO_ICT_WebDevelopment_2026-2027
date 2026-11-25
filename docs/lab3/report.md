# Лабораторная работа № 3

Левахин Лев Александрович, К3340

Вариант 19 · Зоопарк

Работа посвящена учёту животных, размещения и аренды в зоопарке

Сервер хранит данные в PostgreSQL и отдаёт их через Django REST Framework. В реестре можно открыть карточку животного, назначить ему сотрудников, записать сезон зимовки и посмотреть, какие животные живут в том же здании

## Модель данных

| Таблица | Назначение |
|---|---|
| `Animal` | Учётный номер, кличка, пол, дата рождения, вид, зона обитания, владелец, текущий вольер, сведения о покупке и индивидуальные заметки |
| `Species` | Научное и обычное название, класс, группа отчёта, общие характеристики и нормальная температура для рептилий |
| `BirdWintering`, `ReptileHibernation` | Сезонные периоды конкретного животного, включая незакрытый текущий период |
| `HabitatZone` | Название природной зоны, материк, страна и описание |
| `Department`, `Building`, `Enclosure` | Отделы, сезонные здания и вольеры с вместимостью и оснащением |
| `Employee`, `CareAssignment` | Смотрители, ветеринары и закрепление сотрудников за животными |
| `Diet`, `DietAssignment` | Рационы и история их назначения |
| `Zoo`, `Lease` | Зоопарки, сторона-владелец, сторона-получатель, условия и фактические даты аренды |

Научное название вида и учётный номер животного уникальны. Животные одного вида используют общие характеристики из `Species`. Группа отчёта хранится у вида, поскольку «хищники» и «птицы» в задании служат категориями учёта

При добавлении зимовки или спячки API проверяет класс животного, порядок дат и пересечение периодов. Следующий сезон хранится отдельной строкой. Совпадающие границы сезонных периодов считаются пересечением, для назначения рациона конец одного периода может совпадать с началом следующего

У вольера есть отдел и необязательное здание того же отдела. Вольер считается общим при вместимости больше одного. При пересадке в пределах отдела проверяется число занятых мест. Передача и возврат по аренде меняют размещение и состояние договора в одной транзакции. Для заселения запись вольера блокируется до завершения операции

### Связь многие ко многим

За Ивой могут ухаживать смотритель и ветеринар. При этом тот же смотритель может отвечать и за Камыша. Каждое такое назначение хранится отдельной строкой в `CareAssignment`

| Животное | Сотрудник |
|---|---|
| Ива | Анна Ветрова |
| Ива | Илья Орлов |
| Камыш | Анна Ветрова |

У записи `CareAssignment` два внешних ключа. Вместе они образуют уникальную пару, поэтому одного сотрудника нельзя дважды закрепить за одним питомцем

```python
class CareAssignment(models.Model):
    animal = models.ForeignKey(
        Animal, models.CASCADE, related_name="care_assignments",
    )
    employee = models.ForeignKey(
        Employee, models.CASCADE, related_name="care_assignments",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["animal", "employee"],
                name="unique_care_assignment",
            ),
        ]
```

В модели `Animal` поле `employees` использует эту таблицу через параметр `through`

```python
employees = models.ManyToManyField(
    Employee, through="CareAssignment", related_name="animals",
)
```

`animal.employees` выбирает сотрудников животного. Обратное имя `animals` позволяет тем же способом получить питомцев сотрудника. Через `care_assignments` доступны сами записи о закреплении

```python
animal = Animal.objects.get(inventory_number="001")
keeper = Employee.objects.get(personnel_number="С-01")

animal.employees.filter(role=Employee.Role.VET)
keeper.animals.all()
animal.care_assignments.select_related("employee")
```

В API назначение создаётся отдельно запросом `POST /api/care-assignments/`. В теле передаются идентификаторы животного и сотрудника. Чтобы снять назначение, удаляется строка `CareAssignment` по её идентификатору

```json
{
  "animal": 1,
  "employee": 2
}
```

Карточка животного возвращает данные сотрудников вложенным списком. Поле доступно для чтения, а запись связи идёт через ресурс назначений

```python
class AnimalSerializer(CheckedSerializer):
    employees = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Animal
        fields = "__all__"
```

При чтении списка животных `prefetch_related("employees")` заранее загружает сотрудников для всех выбранных питомцев. Для вида и вольера используется `select_related()`, поскольку у животного по одному внешнему ключу на каждый из них

```python
queryset = (
    models.Animal.objects
    .select_related("species", "enclosure")
    .prefetch_related("employees")
    .order_by("id")
)
```

### Связь один ко многим

У отдела может быть несколько вольеров, а у вольера один отдел. Достаточно внешнего ключа `Enclosure.department`. Благодаря `related_name="enclosures"` из отдела можно получить все вольеры через `department.enclosures.all()`. Этот же путь используется во вложенном ответе `GET /api/departments/{id}/`

### Отчёт по аренде

Действующая аренда начинается с фактической передачи животного и заканчивается после возврата. Для исходящей аренды сначала выбираются договоры, где наш зоопарк выступает арендодателем. Затем записи группируются по группе вида или по зоопарку-получателю

```python
leases = models.Lease.objects.filter(
    lessor__is_local=True,
    transferred_at__isnull=False,
    returned_at__isnull=True,
)
by_group = leases.values("animal__species__report_group").annotate(
    animal_count=Count("animal_id", distinct=True),
    total_cost=Sum("total_cost", default=0),
)
```

На демонстрационных данных одна исходящая аренда на 24 000 ₽ и одна входящая на 18 000 ₽. После возврата животного соответствующий договор исчезает из сводки действующих аренд

## Запуск

Нужны Python 3.11+ и PostgreSQL. Создайте пустую базу `zoo` и задайте подключение. Пример для PowerShell из папки `laboratory_work_3`

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
$env:PGDATABASE = "zoo"
$env:PGUSER = "postgres"
$env:PGPASSWORD = "<пароль PostgreSQL>"
.venv/Scripts/python.exe manage.py migrate
.venv/Scripts/python.exe manage.py seed_demo
.venv/Scripts/python.exe manage.py runserver
```

`PGHOST` и `PGPORT` по умолчанию равны `127.0.0.1` и `5432`. Команда `seed_demo` заполняет пустую базу примерами и выполняется один раз. Интерфейс доступен на `http://127.0.0.1:8000/`. В интерфейсе можно зарегистрироваться, войти, работать с реестром и справочниками, оформлять аренду и смотреть отчёты

## API

Запросы к реестру и практикам требуют заголовок `Authorization: Token <auth_token>`. Для учебной версии зарегистрированные пользователи имеют одинаковые права на работу с реестром

| Метод и путь | Назначение |
|---|---|
| `POST /api/auth/users/` | Регистрация по имени пользователя и паролю |
| `POST /api/auth/token/login/` | Вход и получение токена |
| `GET /api/auth/users/me/` | Текущий пользователь |
| `POST /api/auth/token/logout/` | Выход |
| `GET /api/departments/{id}/` | Отдел с вложенными вольерами, связь 1:N |
| `GET /api/animals/{id}/` | Животное с вложенными сотрудниками, связь M:N |
| `GET /api/animals/{id}/building-neighbors/` | Остальные животные в том же здании, пустой список для вольера без здания |
| `POST /api/leases/{id}/transfer/` | Передача животного в срок договора |
| `POST /api/leases/{id}/return/` | Возврат животного по действующему договору |
| `GET /api/reports/department-counts/` | Число животных по отделам, включая пустые отделы |
| `GET /api/reports/shared-enclosures/` | Животные, размещённые в общих вольерах |
| `GET /api/reports/empty-enclosures/` | Пустые вольеры |
| `GET /api/reports/incoming-leases/` | Количество и стоимость действующих входящих аренд по владельцам |
| `GET /api/reports/outgoing-leases/` | Количество и стоимость исходящих аренд по группам, по зоопаркам и общий итог |

Ресурсы CRUD под `/api/` - `animals`, `species`, `habitat-zones`, `departments`, `buildings`, `enclosures`, `employees`, `care-assignments`, `diets`, `diet-assignments`, `zoos`, `leases`, `bird-winterings`, `reptile-hibernations`. `GET` и `POST` работают с коллекцией, `GET`, `PUT`, `PATCH` и `DELETE` с отдельной записью. Ссылки при записи передаются как ID. Исполненный договор сохраняется в истории. При операции аренды, когда животное прибывает в наш зоопарк, в теле запроса указывается `{"enclosure": 1}`

В отчёт включаются переданные и ещё не возвращённые животные. Стоимость считается в рублях по полной сумме договора

## Практики

### 3.1 · Запросы ORM

`python manage.py practice_31` создаёт 7 владельцев, 6 машин, удостоверения и записи владения. Команда выполняет фильтрацию по марке, имени, цвету и году начала владения, ищет удостоверение владельца и выводит агрегаты

Ассоциативная модель `Ownership` хранит дату начала владения. `related_name` задаёт обратный путь, поэтому `ownerships__started_on__year` в запросе к владельцам проходит через записи владения. `distinct()` позволяет получить владельца один раз, даже если условию удовлетворяют несколько его машин

```python
owners.filter(ownerships__started_on__year=2010).distinct()
owners.filter(cars__color="красный").distinct()
owners.annotate(car_count=Count("cars", distinct=True)).values("id", "car_count")
```

В первом запросе фильтр накладывается на дату в таблице владения, во втором используется цвет из таблицы автомобилей. В третьем запросе `annotate()` добавляет число машин к каждому владельцу

### 3.2 · Django REST Framework

| Метод и путь | Результат |
|---|---|
| `GET, POST /api/practice/skills/` | Просмотр и создание умений через `APIView` |
| `GET /api/practice/warriors/professions/` | Воины с профессиями |
| `GET /api/practice/warriors/skills/` | Воины с умениями и уровнем владения |
| `GET, PUT, PATCH, DELETE /api/practice/warriors/{id}/` | Просмотр, редактирование и удаление воина через generic view |

Для изменения профессии передаётся `profession_id`. Для вложенных связей `select_related()` загружает связанные записи с внешним ключом, а `prefetch_related()` подгружает коллекции без отдельного запроса на каждого воина или питомца

У воина может быть несколько умений. Уровень освоения хранится в `SkillOfWarrior`, потому что для одного и того же умения он разный у разных воинов. Поэтому сериализатор читает `skill_links` и возвращает и само умение, и уровень

```python
class SkillLinkSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()

    class Meta:
        model = SkillOfWarrior
        fields = ["skill", "level"]
```

## Проверка

`python manage.py test` проверяет регистрацию, токен, вложенные ответы, аналитику, новые сезоны, передачу и возврат по аренде и эндпоинты практики 3.2
