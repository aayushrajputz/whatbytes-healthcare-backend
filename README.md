# Healthcare Backend API

A production-grade Django & Django REST Framework API for managing **Patients**, **Doctors**, and **Patient–Doctor Mappings**, secured with JWT authentication.

## Tech Stack

- Python 3.10+, Django 5.x, Django REST Framework
- **PostgreSQL** (SQLite fallback for local development via `.env`)
- JWT auth via `djangorestframework-simplejwt`
- API docs via `drf-spectacular` (Swagger UI / ReDoc)
- CORS via `django-cors-headers`, env config via `python-dotenv`

## Project Structure

```
whatbytes-healthcare/
├── healthcare/          # Django project (settings, urls, wsgi/asgi)
├── authentication/      # Register / Login / Token refresh
├── patients/            # Patient CRUD (scoped to owner)
├── doctors/             # Doctor CRUD
├── mappings/            # Patient-Doctor mapping
├── manage.py
├── requirements.txt
├── .env.example
└── postman_collection.json
```

## Setup Instructions

### 1. Clone & enter the project

```bash
cd whatbytes-healthcare
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`. PostgreSQL is the default:

```env
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://healthcare:healthcare@localhost:5432/healthcare
```

**Start PostgreSQL** (matches the credentials above):

```bash
docker compose up -d db
```

Or point `DATABASE_URL` at any existing Postgres instance:

```env
DATABASE_URL=postgres://user:password@host:5432/dbname
```

**For local dev without PostgreSQL**, use SQLite instead:

```env
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

API base URL: `http://127.0.0.1:8000/api/`

### API Documentation

- Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/
- ReDoc: http://127.0.0.1:8000/api/schema/redoc/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

---

## Authentication

All endpoints except `/api/auth/register/`, `/api/auth/login/`, and `/api/auth/token/refresh/` require a JWT access token:

```
Authorization: Bearer <access_token>
```

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr Smith",
    "email": "smith@clinic.com",
    "password": "SecurePass123"
  }'
```

**Response `201 Created`:**

```json
{
  "user": {
    "id": 1,
    "name": "Dr Smith",
    "username": "smith@clinic.com",
    "email": "smith@clinic.com",
    "date_joined": "2026-11-25T15:36:48.791276Z"
  },
  "refresh": "eyJhbGciOi...",
  "access": "eyJhbGciOi..."
}
```

### Login (email or username)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "smith@clinic.com",
    "password": "SecurePass123"
  }'
```

**Response `200 OK`:** same shape as register (`user`, `refresh`, `access`).

`identifier` accepts either the email address or the username (the email is used as the username at registration). You may also send `"email": "..."` instead of `"identifier"`.

### Refresh access token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{ "refresh": "<refresh_token>" }'
```

**Response `200 OK`:**

```json
{ "access": "eyJhbGciOi..." }
```

---

## Patients

Patients are **private to their creator** — list/retrieve/update/delete only ever returns patients where `created_by = <you>`.

### Create patient

```bash
curl -X POST http://127.0.0.1:8000/api/patients/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 45,
    "gender": "Male",
    "contact_number": "+1 555 123 4567",
    "address": "123 Main St"
  }'
```

`gender` must be one of: `"Male"`, `"Female"`, `"Other"`. `address` is optional. `created_by` is set automatically from the JWT user.

**Response `201 Created`:**

```json
{
  "id": "6fc2f529-2f78-42aa-bcdf-7b924c18c1c2",
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "contact_number": "+1 555 123 4567",
  "address": "123 Main St",
  "created_by": 1,
  "created_at": "2026-11-25T15:22:55.678463Z",
  "updated_at": "2026-11-25T15:22:55.678463Z"
}
```

### List patients (only your own)

```bash
curl http://127.0.0.1:8000/api/patients/ \
  -H "Authorization: Bearer <access_token>"
```

### Retrieve / update / delete

```bash
# Retrieve
curl http://127.0.0.1:8000/api/patients/<patient_uuid>/ \
  -H "Authorization: Bearer <access_token>"

# Update (PUT — full update; PATCH also supported)
curl -X PUT http://127.0.0.1:8000/api/patients/<patient_uuid>/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{ "name": "John Updated", "age": 46, "gender": "Male", "contact_number": "+1 555 123 4567" }'

# Delete
curl -X DELETE http://127.0.0.1:8000/api/patients/<patient_uuid>/ \
  -H "Authorization: Bearer <access_token>"
```

Accessing another user's patient returns `404` (owner-scoped queryset).

---

## Doctors

Doctors are shared across all authenticated users.

### Create doctor

```bash
curl -X POST http://127.0.0.1:8000/api/doctors/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Alice",
    "specialization": "Cardiology",
    "email": "alice@hospital.com",
    "phone_number": "+1 555 999 0000"
  }'
```

**Response `201 Created`:**

```json
{
  "id": "6e6f9ac9-a47a-4b31-b14c-a8821994063a",
  "name": "Dr. Alice",
  "specialization": "Cardiology",
  "email": "alice@hospital.com",
  "phone_number": "+1 555 999 0000",
  "created_at": "2026-11-25T15:22:45.241618Z",
  "updated_at": "2026-11-25T15:22:45.241618Z"
}
```

### List / retrieve / update / delete

```bash
curl http://127.0.0.1:8000/api/doctors/ -H "Authorization: Bearer <access_token>"
curl http://127.0.0.1:8000/api/doctors/<doctor_uuid>/ -H "Authorization: Bearer <access_token>"
curl -X PUT http://127.0.0.1:8000/api/doctors/<doctor_uuid>/ -H "Authorization: Bearer <access_token>" -H "Content-Type: application/json" -d '{ ... }'
curl -X DELETE http://127.0.0.1:8000/api/doctors/<doctor_uuid>/ -H "Authorization: Bearer <access_token>"
```

---

## Patient–Doctor Mappings

### Assign a doctor to a patient

```bash
curl -X POST http://127.0.0.1:8000/api/mappings/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "<patient_uuid>",
    "doctor_id": "<doctor_uuid>"
  }'
```

**Response `201 Created`:**

```json
{
  "id": 2,
  "patient_id": "dbc14e1d-8840-482c-9ab8-cc5fc7cc93e9",
  "doctor_id": "6e6f9ac9-a47a-4b31-b14c-a8821994063a",
  "assigned_at": "2026-11-25T15:23:27.550560Z"
}
```

Rules enforced:
- A doctor cannot be mapped to the same patient twice → `400` with a uniqueness error.
- You can only map doctors to patients **you created** → `400` otherwise.

### List mappings (for your patients)

```bash
curl http://127.0.0.1:8000/api/mappings/ \
  -H "Authorization: Bearer <access_token>"
```

### Get all doctors assigned to a patient

```bash
curl http://127.0.0.1:8000/api/mappings/<patient_uuid>/ \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:** array of doctor objects.

### Remove a mapping

```bash
curl -X DELETE http://127.0.0.1:8000/api/mappings/<mapping_id>/ \
  -H "Authorization: Bearer <access_token>"
```

Returns `204 No Content`.

---

## Error Responses

Validation errors return `400` with field-level details:

```json
{
  "age": ["Ensure this value is greater than or equal to 0."]
}
```

Unauthenticated requests return `401`:

```json
{ "detail": "Authentication credentials were not provided." }
```

Not found / not owned returns `404`.

## Architectural Highlights

- **Idempotent mapping transactions** — patient–doctor mapping creation runs inside `transaction.atomic()`; duplicate assignments are rejected with `400` (both via serializer validation and an `IntegrityError` safety net for concurrent requests) instead of `500`s.
- **Cascade protection (`PROTECT`)** — `PatientDoctorMapping.doctor` uses `on_delete=PROTECT`, so deleting a doctor with active mappings is blocked with a clear `400` rather than silently destroying patient assignments.
- **Scoped ownership verification** — patients and mappings are strictly scoped to `created_by = request.user`; cross-user access returns `404`, and mapping creation validates patient ownership before saving.
- **DRF pagination** — global `PageNumberPagination` (`PAGE_SIZE = 10`) keeps list endpoints bounded as data grows.
- **Least-privilege permissions** — doctor reads are open to any authenticated user, while writes require staff (`IsAdminOrReadOnly`).
- **JWT hardening** — refresh-token rotation with blacklist-after-rotation, plus anon/user rate throttling on all endpoints.

## Postman

Import `postman_collection.json` into Postman. Set the `base_url` and `access_token` collection variables after logging in.
