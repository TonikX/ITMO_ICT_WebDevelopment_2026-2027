# Laboratory work 3. Django REST Framework clinic API

**Student:** Fedorova Maria  
**Group:** K3339  
**Variant:** 10 — Medical clinic

---

## Goal

Build a REST API with Django, Django REST Framework, Djoser token auth and PostgreSQL. Cover the clinic domain, analytical queries from the assignment, MkDocs documentation and a React client (same folder architecture as Lab 2).

---

## Variant summary

The system stores doctors, work schedules, cabinets, price-list services, patients (medical cards) and paid appointments. After each visit the patient pays for the service separately.

Implemented operations:

1. User registration / login via **Djoser** (`/api/auth/`)
2. CRUD for doctors, patients, cabinets, services, appointments
3. Mark appointment as paid
4. Analytical endpoints listed in the variant
5. Staff report for doctors in a date range

---

## Architecture

| Layer | Stack |
| ----- | ----- |
| Backend | Django 6 + DRF + Djoser (Token) |
| Database | PostgreSQL (`tours_db`, schema `clinic`) |
| Frontend | React (Vite) + axios + SCSS |
| Docs | MkDocs |

```text
Lr3/
├── backend/     # Django API (clinic app)
├── frontend/    # React client
├── practice/    # Practice 3.1 (cars ORM) + 3.2 (warriors DRF)
└── docs/        # MkDocs report
```

---

## Data model

### Doctor

- FIO, specialty, education, gender, birth date
- work_start / work_end, employment contract number and date
- related schedules (`related_name="schedules"`)

### DoctorSchedule

- weekday (0–6), `is_working`

### Cabinet

- number, work hours, responsible doctor, internal phone

### Service

- price-list item: name, specialty, price

### Patient

- medical card: FIO, birth date, gender, phone, address, passport, card_number

### Appointment

- patient, doctor, cabinet, service
- visited_at, diagnosis, condition, recommendations
- cost (copied from service), `is_paid`

---

## Auth (Djoser)

| Method | URL | Purpose |
| ------ | --- | ------- |
| POST | `/api/auth/users/` | register |
| POST | `/api/auth/token/login/` | get token (`auth_token`) |
| GET | `/api/auth/users/me/` | current user |
| GET | `/api/me/` | same profile via clinic app |

Client stores token and sends `Authorization: Token <key>`.

---

## API endpoints

Base prefix: `/api/`

| Method | URL | Access | Purpose |
| ------ | --- | ------ | ------- |
| GET/POST | `/doctors/` | GET all / POST staff | doctors |
| GET/PATCH/DELETE | `/doctors/<id>/` | GET all / write staff | doctor detail |
| GET/POST | `/patients/` | auth | patients |
| GET/POST | `/appointments/` | auth | visits |
| PATCH | `/appointments/<id>/pay/` | auth | mark paid |
| GET/POST | `/services/`, `/cabinets/` | mixed | dictionaries |
| GET | `/analytics/doctor-patients/?doctor=` | auth | patients of a doctor |
| GET | `/analytics/ent-patients/` | auth | ENT patients born after 1987 |
| GET | `/analytics/doctors-by-weekday/?weekday=` | auth | doctors working that day |
| GET | `/analytics/appointments-by-date/` | auth | counts by date |
| GET | `/analytics/costs/` | auth | sums by day and doctor |
| GET | `/analytics/paid-patients/` | auth | patients who paid |
| GET | `/analytics/doctors-report/?from=&to=` | staff | income report |

---

## Frontend pages

Same layout style as Lab 2 (`pages/`, `components/`, `context/AuthContext/`, SCSS):

- `/` — doctors catalog (search, filter, pagination)
- `/doctors/:id` — doctor card + schedule
- `/patients` — list + create medical card
- `/appointments` — visits, create, pay
- `/analytics` — all analytical queries + staff report
- `/login`, `/register` — Djoser auth

---

## Practice 3.1 / 3.2

Folder `practice/`:

- `practice_3_1/` — автомобили из практики 2.1: ORM create / filter / aggregate (`orm_queries.py`)
- `practice_3_2/` — воины: DRF serializers, CRUD, `related_name` / m2m

See `practice/README.md`.

---

## Run

### Backend

```bash
source /path/to/.venv/bin/activate
cd students/k3339/Fedorova_Maria/Lr3/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_clinic
python manage.py runserver
```

Demo users after seed:

| Login | Password | Role |
| ----- | -------- | ---- |
| `admin` | `admin123` | admin (full access) |
| `manager` | `manager123` | staff |
| `doctor` | `doctor123` | doctor (ENT Smirnova) |
| `patient` | `patient123` | patient (Petrova) |

Roles:

- **Guest / new user** — doctors catalog; after register can create own medical card
- **Patient** — own appointments + pay
- **Doctor** — own patients / appointments, create visits (forced to self)
- **Admin** — full CRUD + analytics / reports

API: `http://127.0.0.1:8000/api/`

### Frontend

```bash
cd students/k3339/Fedorova_Maria/Lr3/frontend
npm install
npm run dev
```

Client: `http://127.0.0.1:5173`

### MkDocs

```bash
cd students/k3339/Fedorova_Maria/Lr3
mkdocs serve
```

### Tests

```bash
cd backend && python manage.py test clinic
cd ../practice/practice_3_1 && python manage.py test
cd ../practice_3_2 && python manage.py test
```

---

## PostgreSQL note

Tables live in schema `clinic` inside PostgreSQL database `tours_db` (user `tours_user`) so Lab 2 and Lab 3 stay isolated without a separate superuser database. Settings use `search_path=clinic,public`.
