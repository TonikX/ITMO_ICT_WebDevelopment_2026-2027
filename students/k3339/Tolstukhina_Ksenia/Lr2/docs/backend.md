# Реализация серверной части

Серверная сторона: модели, формы, представления, маршрутизация, административная панель. Клиентская
часть – шаблоны Bootstrap

Структура приложения `races/`:

```text
races/
├── models.py         # модели данных
├── forms.py          # формы
├── views.py          # представления (FBV и CBV)
├── urls.py           # маршруты приложения
├── admin.py          # настройка Django-admin
├── migrations/       # миграции
└── templates/races/  # шаблоны
```

---

## 1. Маршрутизация (`races/urls.py`)

Маршруты приложения сгруппированы по функциональности. Все они
подключены в корневом `racing_site/urls.py` через
`path("", include("races.urls"))` с `app_name = "races"` — это
позволяет строить URL через `{% url 'races:race_detail' pk %}`.

### Группа «Аутентификация»

| URL          | Имя        | View         | Назначение                            |
|--------------|------------|--------------|---------------------------------------|
| `/register/` | `register` | `register`   | Регистрация нового пользователя       |
| `/login/`    | `login`    | `LoginView`  | Вход (из `django.contrib.auth.views`) |
| `/logout/`   | `logout`   | `LogoutView` | Выход (POST-форма в навбаре)          |

### Группа «Профиль»

| URL               | Имя              | View             |
|-------------------|------------------|------------------|
| `/profile/`       | `profile`        | `profile`        |
| `/profile/edit/`  | `profile_edit`   | `profile_edit`   |
| `/user/<int:pk>/` | `public_profile` | `public_profile` |

### Группа «Гонки»

| URL                               | Имя             | View               |
|-----------------------------------|-----------------|--------------------|
| `/`                               | `race_list`     | `RaceListView`     |
| `/race/<int:pk>/`                 | `race_detail`   | `RaceDetailView`   |
| `/race/create/`                   | `race_create`   | `RaceCreateView`   |
| `/race/<int:pk>/edit/`            | `race_edit`     | `RaceUpdateView`   |
| `/race/<int:race_pk>/result/add/` | `result_create` | `ResultCreateView` |

### Группа «Регистрация на гонку»

| URL                              | Имя                    | View                   |
|----------------------------------|------------------------|------------------------|
| `/race/<int:pk>/register/`       | `register_for_race`    | `register_for_race`    |
| `/registration/<int:pk>/delete/` | `unregister_from_race` | `unregister_from_race` |

### Группа «Комментарии и табло»

| URL                       | Имя             | View             |
|---------------------------|-----------------|------------------|
| `/race/<int:pk>/comment/` | `add_comment`   | `add_comment`    |
| `/results/`               | `results_table` | `results_table`  |
| `/participants/`          | `participants`  | `participants`   |
| `/auto/create/`           | `auto_create`   | `AutoCreateView` |

---

## 2. Формы (`forms.py`)

Все формы наследуют от общего миксина **`BootstrapFormMixin`**,
который автоматически навешивает нужные CSS-классы на поля. 
Это избавляет от ручного прописывания `widgets = {...}` в каждой форме

```python
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                cls = "form-check-input"
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                cls = "form-select"
            else:
                cls = "form-control"
            w.attrs["class"] = (w.attrs.get("class", "") + " " + cls).strip()
```

Логика в миксине:

- чекбокс → `form-check-input`;
- `<select>` и `<select multiple>` → `form-select`;
- всё остальное (`text`, `email`, `date`, `number`, `textarea`) → `form-control`.

### `UserRegistrationForm`

```python
class UserRegistrationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email","team", "birthday", "driving_experience", "racer_class")
```

- Наследуется от `UserCreationForm` — Django сам добавляет поля `password1` / `password2` и валидацию пароля по `AUTH_PASSWORD_VALIDATORS`
- Дополнительно к стандартным `username/first_name/last_name` расширена полями профиля гонщика (`team`, `birthday`, `driving_experience`, `racer_class`)
- `email` явно помечен как `required=True` — в стандартной форме Django он необязательный

### `UserProfileForm`

```python
class UserProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email","team", "birthday", "driving_experience", "racer_class")
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }
```

`ModelForm` только для профильных полей — `username` менять нельзя. Используется на `/profile/edit/`  
Поле `birthday` получает `widget=DateInput(attrs={"type": "date"})`, чтобы браузер показал нативный date-picker

### `AutoForm`

```python
class AutoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Auto
        fields = ("state", "make", "model", "color")
        widgets = {
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "А123БВ777"}),
            "make": forms.TextInput(attrs={"class": "form-control", "placeholder": "Toyota"}),
            "model": forms.TextInput(attrs={"class": "form-control", "placeholder": "Supra"}),
            "color": forms.TextInput(attrs={"class": "form-control", "placeholder": "Красный"}),
        }
```
`ModelForm` для модели `Auto` с полями `state / make / model / color`

### `CommentForm`

```python
class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text", "race_date", "comment_type", "rating")
        widgets = {
            "race_date": forms.DateInput(attrs={"type": "date"}),
            "text": forms.Textarea(attrs={"rows": 4}),
        }
```

- Поля `user` нет в форме — берётся из `request.user`
- `rating` валидируется на уровне модели (`MinValueValidator(1)`, `MaxValueValidator(10)`)
- `race_date` по умолчанию инициализируется датой гонки

### `ResultForm`

Зависимые поля: гонщик → автомобиль

```python
class ResultForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Result
        fields = ("user", "auto", "duration")
        widgets = {
            "duration": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "ЧЧ:ММ:СС, например 00:12:34",
            }),
            "user": forms.Select(attrs={"class": "form-select", "id": "id_user"}),
            "auto": forms.Select(attrs={"class": "form-select", "id": "id_auto"}),
        }

    def __init__(self, *args, race=None, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Участники — только зарегавшиеся на ЭТУ гонку
        if race is not None:
            self.fields["user"].queryset = User.objects.filter(
                registrations__race=race,
                registrations__deleted_at__isnull=True,
            ).distinct().order_by("last_name", "first_name")
        else:
            self.fields["user"].queryset = User.objects.none()
        self.fields["user"].empty_label = "— выберите участника —"

        # Машины — только выбранного участника
        if user_id:
            autos = Auto.objects.filter(owner_id=user_id, deleted_at__isnull=True)
        else:
            autos = Auto.objects.none()
        self.fields["auto"].queryset = autos
        if autos.count() == 1:
            self.fields["auto"].initial = autos.first()
        self.fields["auto"].empty_label = "— сначала выберите участника —"
```

- Список гонщиков – только те, кто зарегистрирован на эту гонку (`registrations__race=race`) и 
  чья регистрация не удалена (`registrations__deleted_at__isnull=True`). `.distinct()` нужен,
   потому что `JOIN` по `registrations` даёт дубликаты
- Список автомобилей – только машины выбранного пользователя (`owner_id=user_id`)
- Если у пользователя одна машина – она сразу подставляется как `initial`, чтобы администратор не выбирал
- Параметр `user_id` приходит во view из GET или POST

## 3. Представления (`views.py`)

### Общие миксины

`StaffRequiredMixin` — пускает только `is_staff`:

```python
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "Доступ только для администраторов.")
        return redirect("races:race_list")
```

Наследуется от `UserPassesTestMixin`; при неудаче — редирект с флеш-сообщением

Применяется к `RaceCreateView`, `RaceUpdateView`, `ResultCreateView`

### Функциональные представления (FBV)

#### `register`

Стандартный паттерн «форма → валидация → save → redirect». При успехе — сообщение и редирект на `/login/`. При ошибке — рендер формы с ошибками

#### `profile` и `profile_edit`

- `profile` — только GET, отдаёт профиль, форму авто для модалки и `my_results`, сортировка по `duration`
- `profile_edit` — GET/POST на `UserProfileForm`

Обе защищены `@login_required`

#### `public_profile`

```python
def public_profile(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    registrations = user_obj.registrations.select_related("race").all()
    results = user_obj.results.select_related("race", "auto").order_by("duration")
    comments = user_obj.comments.select_related("race").all()
    return render(request, "races/public_profile.html", {
        "profile_user": user_obj,
        "registrations": registrations,
        "results": results,
        "comments": comments,
    })
```

`select_related` подтягивает связанные объекты одним JOIN'ом

#### `participants`

Пагинация через `Paginator`:

```python
def participants(request):
    users = User.objects.filter(is_staff=False).order_by("last_name", "first_name")
    paginator = Paginator(users, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "races/participants.html", {"page_obj": page_obj})
```

#### `register_for_race` и `unregister_from_race`

Регистрация — POST-only, с проверкой на дубликат. Отмена — soft delete через `timezone.now()`, физически запись остаётся в БД:

```python
@login_required
def unregister_from_race(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user, deleted_at__isnull=True)
    race_pk = registration.race.pk
    registration.deleted_at = timezone.now()
    registration.save(update_fields=["deleted_at"])
    messages.success(request, "Регистрация удалена.")
    return redirect("races:race_detail", pk=race_pk)
```

Условие `user=request.user` не даёт отменить чужую регистрацию по прямому URL

#### `add_comment`

Проверка `is_valid` и установка `user` / `race` в обход формы, из `request.user` и URL. При ошибке валидации — флеш-сообщение, а не рендер формы, потому что форма живёт в модалке

#### `results_table`

```python
def results_table(request):
    races = Race.objects.prefetch_related(Prefetch("results", queryset=Result.objects.filter(deleted_at__isnull=True).select_related("user", "auto").order_by("duration"), to_attr="sorted_results"),).order_by("-date")
    return render(request, "races/results_table.html", {"races": races})
```

- `Prefetch` с `to_attr` подгружает результаты одним запросом и кладёт их в `race.sorted_results` – отдельный список, чтобы не мешать стандартному `race.results`
- `.order_by("duration")` – сортировка по возрастанию, лучший первым
- `select_related("user", "auto")` – JOIN на пользователя и авто
- Внешний `.order_by("-date")`

### Классовые представления (CBV)

#### `RaceListView`

```python
class RaceListView(ListView):
    model = Race
    template_name = "races/race_list.html"
    context_object_name = "races"
    paginate_by = 9

    def get_queryset(self):
        qs = Race.objects.all().order_by("-date")
        q = self.request.GET.get("q")
        loc = self.request.GET.get("location")
        if q:
            qs = qs.filter(name__icontains=q)
        if loc:
            qs = qs.filter(location__icontains=loc)
        return qs
```

- `paginate_by = 9` – Django сам разбивает queryset на страницы и кладёт в контекст `page_obj`
- `get_queryset` реализует поиск по названию и месту через `icontains`
- GET-параметры `q` / `location` сохраняются в `_pagination.html`

#### `RaceDetailView`

```python
class RaceDetailView(DetailView):
    model = Race
    template_name = "races/race_detail.html"
    context_object_name = "race"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.object
        context["registrations"] = race.registrations.select_related("user").filter(deleted_at__isnull=True).all()
        context['results'] = race.results.select_related('user', 'auto').filter(deleted_at__isnull=True).all().order_by("duration")
        context['comments'] = race.comments.select_related('user').filter(deleted_at__isnull=True).all()
        context["comment_form"] = CommentForm(initial={"race_date": race.date})
        if self.request.user.is_authenticated:
            context["my_registration"] = race.registrations.filter(user=self.request.user, deleted_at__isnull=True).first()
        return context
```

- Один GET-запрос на страницу – все связанные данные подтягиваются одним `select_related`
- `my_registration` используется в шаблоне, чтобы отрисовать
  либо кнопку «Зарегистрироваться», либо бейдж «Вы зарегистрированы»
  с кнопкой «Отменить»

#### `RaceCreateView` / `RaceUpdateView`

```python
class RaceCreateView(StaffRequiredMixin, CreateView):
    model = Race
    fields = ["name", "description", "date", "start_time", "end_time", "location"]
    template_name = "races/race_form.html"
    success_url = reverse_lazy("races:race_list")

    def form_valid(self, form):
        messages.success(self.request, f"Гонка «{form.instance.name}» создана.")
        return super().form_valid(form)
```

```python
class RaceUpdateView(StaffRequiredMixin, UpdateView):
    model = Race
    fields = ["name", "description", "date", "start_time", "end_time", "location"]
    template_name = "races/race_form.html"
    success_url = reverse_lazy("races:race_list")
```

#### `ResultCreateView`

Самый сложный CBV — с проверкой бизнес-правил:

```python
class ResultCreateView(StaffRequiredMixin, CreateView):
    model = Result
    form_class = ResultForm
    template_name = "races/result_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.race = get_object_or_404(Race, pk=kwargs["race_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["race"] = self.race
        user_id = self.request.GET.get("user") or self.request.POST.get("user")
        if user_id:
            kwargs["user_id"] = user_id
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        user_id = self.request.GET.get("user")
        if user_id:
            initial["user"] = user_id
        return initial

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        auto = form.cleaned_data["auto"]

        if not Registration.objects.filter(user=user, race=self.race, deleted_at__isnull=True).exists():
            form.add_error("user", "Этот участник не зарегистрирован на гонку.")
            return self.form_invalid(form)

        if auto.owner_id != user.pk:
            form.add_error("auto", "Эта машина не принадлежит выбранному участнику.")
            return self.form_invalid(form)

        form.instance.race = self.race
        messages.success(self.request, "Результат добавлен.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("races:race_detail", kwargs={"pk": self.race.pk})
```

#### `AutoCreateView`

Простой `CreateView` с `LoginRequiredMixin` — владелец авто проставляется автоматически:

```python
class AutoCreateView(LoginRequiredMixin, CreateView):
    model = Auto
    form_class = AutoForm
    template_name = "races/auto_form.html"
    success_url = reverse_lazy("races:profile")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, f"Автомобиль {form.instance} добавлен.")
        return super().form_valid(form)
```

## 4. Django-admin (`admin.py`)

Все модели зарегистрированы с расширенными настройками, администратор работает не только через клиентский интерфейс, но и через стандартную панель

### `User` — расширенный `UserAdmin`

```python
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Гонщик", {"fields": ("racer_class", "team", "birthday", "driving_experience")}),)
    list_display = ("username", "first_name", "last_name", "team", "racer_class", "is_staff", "birthday", "driving_experience")
```

- `fieldsets` дополняют стандартные секции `UserAdmin`
- `list_display` — все ключевые поля видны в списке без перехода в карточку

### `Auto`

```python
@admin.register(Auto)
class AutoAdmin(admin.ModelAdmin):
    list_display = ("state", "make", "model", "color", "owner")
    search_fields = ("state", "make", "model")
```
`list_display` + `search_fields` по `state / make / model` – поиск по госномеру и модели

### `Race`

```python
@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "date", "start_time", "end_time", "location")
    list_filter = ("date", "location")
    search_fields = ("name", "date", "location")
```

`list_filter` по `date` и `location`, `search_fields` по `name / date / location`. `list_display` включает все поля

### `Result`

```python
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "auto", "duration")
    list_filter = ("race", "user")
    search_fields = ("user", "race")
```
`list_filter` по `race` и `user`, `search_fields` по тем же полям

### `Registration`

```python
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "created_at")
    list_filter = ("race", "user")
    search_fields = ("user", "race", "created_at")
```
`list_display` включает `created_at` — видно, когда пользователь зарегистрировался. `list_filter` по гонке и пользователю

### `Comment`

```python
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "race", "text", "race_date", "comment_type", "rating", "created_at")
    list_filter = ("comment_type", "race")
    search_fields = ("text", "user", "race")
```
`list_display` содержит все обязательные по заданию поля. Фильтры по типу и гонке

---

## 5. Шаблоны — кратко

Общий базовый шаблон `base.html` содержит навбар (с проверкой ролей через `{% if user.is_staff %}`), флеш-сообщения и подключение Bootstrap 5 в тёмной теме

Ключевые страницы:

| Шаблон                               | Что содержит                                                                   |
|--------------------------------------|--------------------------------------------------------------------------------|
| `race_list.html`                     | Карточки гонок + поиск + пагинация                                             |
| `race_detail.html`                   | Табы «Участники / Результаты / Комментарии», модалки регистрации и комментария |
| `profile.html`                       | Профиль + модалка добавления авто                                              |
| `results_table.html`                 | Общее табло                                                                    |
| `participants.html`                  | Сетка карточек гонщиков                                                        |
| `public_profile.html`                | Публичный профиль                                                              |
| `profile_edit.html`                  | Редактирование профиля                                                         |
| `race_form.html`, `result_form.html` | Админские формы                                                                |
| `register.html`, `login.html`        | Аутентификация                                                                 |
| `_pagination.html`                   | Partial с пагинацией, сохраняет GET-параметры                                  |
