# Лабораторная работа № 3

Левахин Лев Александрович, К3340

Вариант 19 · Зоопарк

Для работы зоопарка нужно знать, где сейчас находится животное, кто за ним ухаживает и кому оно принадлежит. Эти сведения меняются независимо. Питомца можно пересадить, назначить ему другого смотрителя или временно передать в другой зоопарк. При этом старая запись о зимовке и завершённый договор остаются в базе

Карточка животного связывает эти данные. Например, при передаче животного в другой зоопарк сервер освобождает его вольер и отмечает дату передачи. Отчёт по аренде учитывает этот договор, а список пустых вольеров учитывает освободившееся место, если в вольере больше никого нет

Интерфейс состоит из реестра, справочников, аренды и отчётов. Браузер отправляет запросы в Django REST Framework. Сервер проверяет данные, выполняет операции через Django ORM и возвращает JSON. Данные хранятся в PostgreSQL

```python
path("", TemplateView.as_view(template_name="zoo/index.html")),
path("api/", include("zoo.urls")),
```

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

### Виды и сезонная история

У нескольких питомцев может быть один вид. Например, Ива и Камыш ссылаются на одну крякву в `Species`. Научное название, класс и общие характеристики меняются в справочнике видов. Заметка об уходе хранится у конкретного питомца

```python
species = models.ForeignKey(Species, PROTECT, related_name="animals")
care_notes = models.TextField(blank=True)
```

Запись зимовки ссылается на животное. У Ивы могут быть две строки с разными датами, а у Камыша зимовок пока может не быть. `arrival_date` остаётся пустой до фактического возвращения. Для спячки используется та же схема с полями `starts_on` и `ends_on`

```python
class BirdWintering(models.Model):
    animal = models.ForeignKey(Animal, PROTECT, related_name="winterings")
    wintering_code = models.CharField(max_length=30)
    wintering_country = models.CharField(max_length=80)
    departure_date = models.DateField()
    arrival_date = models.DateField(null=True, blank=True)
```

При записи периода сериализатор блокирует строку животного, проверяет его класс и ищет пересечения только среди его записей. Открытый период учитывается при поиске пересечений. При редактировании текущая строка исключается из сравнения

```python
animal = models.Animal.objects.select_for_update().get(pk=period.animal_id)
if self.animal_class and animal.species.animal_class != self.animal_class:
    raise serializers.ValidationError({"animal": "Период не подходит для класса животного"})

start = getattr(period, self.start_field)
end = getattr(period, self.end_field)
end_filter = models.Q(**{f"{self.end_field}__isnull": True}) | models.Q(
    **{f"{self.end_field}__{self.end_lookup}": start}
)
existing = self.Meta.model.objects.filter(animal=animal).exclude(pk=period.pk).filter(end_filter)
if end is not None:
    existing = existing.filter(**{f"{self.start_field}__{self.start_lookup}": end})
if existing.exists():
    raise serializers.ValidationError({"animal": "Периоды для одного животного пересекаются"})
```

Для рациона связь вынесена в `DietAssignment`, где хранятся даты начала и окончания. После смены рациона прежнее назначение остаётся в истории. Для поиска действующих назначений можно использовать обе границы периода

```python
now = timezone.now()
current_diets = models.DietAssignment.objects.filter(
    animal=animal, started_at__lte=now,
).filter(models.Q(ended_at__isnull=True) | models.Q(ended_at__gt=now))
```


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

### Размещение и пересадка

При пересадке меняется внешний ключ `Animal.enclosure`. Тот же вольер может быть указан у нескольких питомцев, если есть свободные места. Сериализатор проверяет, что новый вольер находится в том же отделе. Запись целевого вольера блокируется, чтобы два одновременных заселения не заняли одно и то же последнее место

```python
enclosure = models.Enclosure.objects.select_for_update().get(pk=animal.enclosure_id)
if current and current.department_id != enclosure.department_id:
    raise serializers.ValidationError({"enclosure": "Пересадка разрешена в пределах отдела"})
if enclosure.animals.exclude(pk=animal.pk).count() >= enclosure.capacity:
    raise serializers.ValidationError({"enclosure": "Вольер заполнен"})
```

Соседей ищем по зданию текущего вольера. Само выбранное животное исключаем из списка. Если у питомца нет вольера или вольер расположен вне здания, сервер возвращает пустой список

```python
animal = self.get_object()
building_id = animal.enclosure.building_id if animal.enclosure else None
neighbors = self.get_queryset().filter(
    enclosure__building_id=building_id,
).exclude(pk=animal.pk)
return Response(self.get_serializer(neighbors if building_id else [], many=True).data)
```

### Передача и возврат по аренде

В договоре датами `starts_on` и `ends_on` задан плановый срок. Поля `transferred_at` и `returned_at` показывают, когда животное действительно передали и вернули. Клиент не заполняет эти поля напрямую, даты ставит сервер при выполнении операций

При исходящей аренде передача освобождает вольер, а для возврата указывается вольер для заселения. При входящей аренде всё наоборот. Изменение договора и размещения входит в одну транзакцию. Если вольер заполнен, операция завершается ошибкой и прежнее состояние сохраняется

```python
@action(detail=True, methods=["post"], url_path="return")
@transaction.atomic
def return_animal(self, request, pk=None):
    lease = get_object_or_404(models.Lease.objects.select_for_update(), pk=pk)
    if not lease.transferred_at or lease.returned_at:
        raise serializers.ValidationError("Сейчас договор не исполняется")
    self.move_animal(lease, request, arriving=lease.lessor.is_local)
    lease.returned_at = timezone.now()
    lease.save(update_fields=["returned_at"])
    return Response(self.get_serializer(lease).data)
```

### Запросы по вольерам и отделам

В сводке по отделам `Count("enclosures__animals")` идёт от отдела к его вольерам и дальше к размещённым животным. Отдел без животных остаётся в ответе с нулём. Для списка пустых вольеров используется обратная связь `animals`, а для общих вольеров проверяется вместимость

```python
department_rows = models.Department.objects.values("id", "name").annotate(
    animal_count=Count("enclosures__animals"),
).order_by("name")
empty = models.Enclosure.objects.filter(animals__isnull=True)
shared = AnimalViewSet.queryset.filter(enclosure__capacity__gt=1)
```


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

## Вход и токены

Djoser предоставляет регистрацию, вход, выход и получение текущего пользователя. Маршруты подключены в `config/urls.py` под общим префиксом `/api/auth/`

```python
path("api/auth/", include("djoser.urls")),
path("api/auth/", include("djoser.urls.authtoken")),
```

В настройках DRF `TokenAuthentication` определяет пользователя по токену, а `IsAuthenticated` требует входа для запросов к реестру. У зарегистрированных пользователей одинаковый доступ к операциям реестра. Роль сотрудника в карточке зоопарка описывает его работу с животными

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}
```

Формы входа и регистрации используют одни поля, имя пользователя и пароль. При регистрации сначала создаётся аккаунт, затем выполняется обычный вход. Djoser проверяет учётные данные и возвращает `auth_token`. Фронтенд сохраняет этот токен в `sessionStorage` текущей вкладки. При перезагрузке страницы он остаётся доступен

```javascript
const data = {username: username.value, password: password.value};
if (register) await api("auth/users/", "POST", data);

const token = await api("auth/token/login/", "POST", data);
setToken(token.auth_token);
await initialize();
```

```javascript
export function getToken() {
  return sessionStorage.getItem("zoo-token");
}

export function setToken(token) {
  if (token) sessionStorage.setItem("zoo-token", token);
  else sessionStorage.removeItem("zoo-token");
}
```

Все запросы из интерфейса проходят через `api()`. Функция добавляет заголовок `Authorization: Token …`. При открытии сайта `initialize()` делает запрос к `/api/auth/users/me/`. Если токен действителен, интерфейс показывает имя пользователя и реестр. Если запрос завершился ошибкой, сохранённый токен удаляется и открывается форма входа

```javascript
const headers = {};
if (getToken()) headers.Authorization = "Token " + getToken();
if (data !== undefined) headers["Content-Type"] = "application/json";

const response = await fetch("/api/" + path, {
  method,
  headers,
  body: data === undefined ? undefined : JSON.stringify(data),
});
```

При выходе Djoser удаляет токен на сервере. В блоке `finally` интерфейс очищает токен во вкладке и возвращается к форме входа, даже если запрос завершился ошибкой

```javascript
try {
  await api("auth/token/logout/", "POST");
} finally {
  setToken(null);
  await initialize();
}
```

### Запросы к API из PowerShell

Пример для локального сервера и уже зарегистрированного пользователя. `Get-Credential` запрашивает данные для входа, поэтому пароль не записан в примере

```powershell
$base = 'http://127.0.0.1:8000/api'
$credentials = Get-Credential
$body = @{
    username = $credentials.UserName
    password = $credentials.GetNetworkCredential().Password
} | ConvertTo-Json

$login = Invoke-RestMethod "$base/auth/token/login/" -Method Post -ContentType 'application/json' -Body $body
$headers = @{ Authorization = "Token $($login.auth_token)" }

Invoke-RestMethod "$base/auth/users/me/" -Headers $headers
Invoke-RestMethod "$base/animals/" -Headers $headers | ConvertTo-Json -Depth 8
Invoke-RestMethod "$base/auth/token/logout/" -Headers $headers -Method Post
```


## API

Запросы к реестру требуют заголовок `Authorization: Token <auth_token>`

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

## Проверка

`python manage.py test` проверяет регистрацию, токен, вложенные ответы, аналитику, новые сезоны, передачу и возврат по аренде

При проверке вложенного ответа сначала находится Ива, затем API возвращает её карточку вместе с двумя сотрудниками. Следующий запрос проверяет, что поиск соседей по зданию находит Камыша

```python
bird = models.Animal.objects.get(name="Ива")
self.assertEqual(
    len(self.client.get(f"/api/animals/{bird.id}/").data["employees"]),
    2,
)
self.assertEqual(
    len(self.client.get(f"/api/animals/{bird.id}/building-neighbors/").data),
    1,
)
```
