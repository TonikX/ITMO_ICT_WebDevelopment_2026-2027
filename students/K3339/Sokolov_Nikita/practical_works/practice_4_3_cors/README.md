# Практика 4.3 — CORS

CORS настроен на серверах, с которыми ходит Vue:

1. **ЛР3 (клиника)** — `laboratory_work_3/clinic_project/settings.py`  
   `django-cors-headers`, origins `http://127.0.0.1:5173` и `localhost:5173`.

2. **Практика warriors** — `warriors_project/warriors_project/settings.py`  
   origins `5173` и `5174` (порт практики 4.2).

Пакет: `django-cors-headers` в `requirements.txt` соответствующих проектов.
