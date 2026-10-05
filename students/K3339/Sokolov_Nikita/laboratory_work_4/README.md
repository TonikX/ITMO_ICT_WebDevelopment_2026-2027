# Лабораторная работа 4 — Вариант 10: лечебная клиника (Vue.js)

Vue 3 + Vite + Vuetify + Pinia + Vue Router. Клиент к API из `laboratory_work_3`.

## Секреты

```bash
cp .env.example .env
```

`VITE_API_BASE_URL` — адрес Django API (по умолчанию `http://127.0.0.1:8000`).

## Запуск бэкенда (ЛР3)

В отдельном терминале:

```bash
brew services start postgresql@16
cd ../laboratory_work_3
source ../laboratory_work_2/.venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

На бэкенде включён CORS для `http://127.0.0.1:5173`.

## Запуск фронтенда

```bash
cd students/K3339/Sokolov_Nikita/laboratory_work_4
npm install
npm run dev
```

Открыть: http://127.0.0.1:5173/

Демо-логин после `seed_clinic`: `admin` / пароль из `.env` ЛР3 (`DEMO_ADMIN_PASSWORD`).

## Интерфейсы

| Страница | Что |
|----------|-----|
| `/login`, `/register` | вход и регистрация (Djoser) |
| `/profile` | изменение email / имени |
| `/doctors`, `/doctors/:id` | CRUD врачей, nested пациенты |
| `/patients`, `/patients/:id` | CRUD пациентов |
| `/visits` | список и создание приёмов |
| `/medical-cards` | карты + nested приёмы |
| `/cabinets`, `/price-list`, `/schedules` | справочники |
| `/analytics` | отчёты варианта 10 |
