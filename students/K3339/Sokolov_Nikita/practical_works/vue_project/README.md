# Практика 4.2 — введение во Vue.js

Vue 3 + Vite + Vue Router + Axios.

- `/hi` — компонент Hello
- `/warriors` — список и создание воинов (локальный `warriors_project`)

## Бэкенд

В отдельном терминале:

```bash
cd students/K3339/Sokolov_Nikita/practical_works/warriors_project
source ../../laboratory_work_2/.venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_warriors
python manage.py runserver 8001
```

На бэкенде включён CORS для портов 5173/5174.

## Фронтенд

```bash
cd students/K3339/Sokolov_Nikita/practical_works/vue_project
cp .env.example .env
npm install
npm run dev
```

http://127.0.0.1:5174/
