# Hospital Management System — REST API

A RESTful API for a Hospital Management System, built with **Django** and
**Django REST Framework (DRF)**, implementing the ERD provided in the
assignment exactly: `User`, `Doctor`, `Patient`, `Department`,
`Appointment`, `Prescription`, `PrescriptionMedicine`, `Medicine`, `Bill`.

## Tech Stack

- Django 5.0
- Django REST Framework
- Simple JWT (`djangorestframework-simplejwt`) for authentication
- django-filter for query filtering
- SQLite (default, zero setup) or PostgreSQL (optional, production-style)

## Project Structure

```
hospital_management_system/
├── config/                # project settings, root urls, custom permissions/exceptions
├── accounts/               # custom User model, register/login/JWT, role management
├── departments/            # Department CRUD
├── doctors/                 # Doctor CRUD, availability
├── patients/                # Patient CRUD
├── appointments/            # Book / view / update / cancel appointments
├── medicines/                # Medicine catalog, list/search
├── prescriptions/            # Prescription + PrescriptionMedicine (multi-medicine support)
├── billing/                   # Generate bills, mark as paid
├── manage.py
├── requirements.txt
└── .env.example
```

## 1. Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd hospital_management_system

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env if needed. By default USE_SQLITE=True, so it works out of the box.

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. (Optional but recommended) seed demo data
python manage.py seed_data

# 7. Create a superuser (skip if you ran seed_data, which creates one: admin / Admin@12345)
python manage.py createsuperuser

# 8. Run the server
python manage.py runserver
```

The API is now live at `http://127.0.0.1:8000/api/v1/`.
Django admin is at `http://127.0.0.1:8000/admin/`.

### Using PostgreSQL instead of SQLite

In `.env`, set:
```
USE_SQLITE=False
DB_NAME=hospital_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```
Then create the database (`createdb hospital_db`) and run the migrate step above.

## 2. Demo Credentials (after `seed_data`)

| Role         | Username        | Password       |
|--------------|-----------------|----------------|
| Admin        | admin           | Admin@12345    |
| Receptionist | receptionist1   | Reception@123  |
| Doctor       | dr_john         | Doctor@123     |
| Doctor       | dr_jane         | Doctor@123     |
| Patient      | patient_mike    | Patient@123    |
| Patient      | patient_amy     | Patient@123    |

## 3. Authentication

JWT-based authentication via Simple JWT. Every protected endpoint requires:

```
Authorization: Bearer <access_token>
```

### Register
`POST /api/v1/auth/register/`
```json
{
  "username": "patient_mike",
  "email": "mike@example.com",
  "password": "Patient@123",
  "password2": "Patient@123",
  "first_name": "Mike",
  "last_name": "Johnson",
  "role": "patient"
}
```
`role` is one of `admin`, `doctor`, `patient`, `receptionist` (defaults to `patient`).

> Note: registering creates the **User** account only. To get a full Doctor
> or Patient profile (with department/specialization or age/blood group
> etc.), an admin/receptionist then calls `POST /api/v1/doctors/` or
> `POST /api/v1/patients/` with `user_id` set to the new user's id — OR
> simply pass the username/email/password directly into those endpoints to
> create the User and profile in one step (see section 5/6 below).

### Login
`POST /api/v1/auth/login/`
```json
{ "username": "patient_mike", "password": "Patient@123" }
```
Response:
```json
{
  "refresh": "...",
  "access": "...",
  "user": { "id": 5, "username": "patient_mike", "role": "patient", ... }
}
```

### Refresh token
`POST /api/v1/auth/login/refresh/`  — body: `{ "refresh": "<refresh_token>" }`

### Logout (blacklist refresh token)
`POST /api/v1/auth/logout/` — body: `{ "refresh": "<refresh_token>" }`

### Current user profile
`GET /api/v1/auth/me/` · `PATCH /api/v1/auth/me/`

### Change password
`POST /api/v1/auth/change-password/`

## 4. Role-Based Permissions Overview

| Resource           | Admin | Receptionist | Doctor                          | Patient                          |
|---------------------|-------|---------------|----------------------------------|------------------------------------|
| Departments          | CRUD  | CRUD          | Read                              | Read                                |
| Doctors               | CRUD  | CRUD          | Read all, update own profile       | Read all (to choose a doctor)        |
| Patients               | CRUD  | CRUD          | Read all (read-only)                | Read/update own record only           |
| Appointments            | CRUD  | CRUD          | Read own, approve/complete/cancel own | Book own, read own, cancel own        |
| Medicines                 | CRUD  | CRUD          | Read                                | Read                                    |
| Prescriptions               | CRUD  | Read          | Create/update/delete own              | Read own only                            |
| Bills                         | CRUD  | CRUD          | No access                              | Read own only                              |

## 5. Doctor & Patient APIs

`GET/POST /api/v1/doctors/` · `GET/PUT/PATCH/DELETE /api/v1/doctors/{id}/`

Filters: `?department=<id>&is_available=true&specialization=Cardiology&search=john`

Create a doctor (admin/receptionist), creating the User at the same time:
```json
{
  "username": "dr_new",
  "email": "new@hospital.com",
  "password": "Doctor@123",
  "first_name": "New",
  "last_name": "Doc",
  "department": 1,
  "specialization": "Dermatology",
  "phone": "01711111111",
  "experience": 3,
  "is_available": true
}
```
Or attach a profile to an existing `role=doctor` user: replace the user fields above with `"user_id": <id>`.

Toggle availability: `PATCH /api/v1/doctors/{id}/set-availability/` — `{ "is_available": false }`

List only available doctors: `GET /api/v1/doctors/available/`

`GET/POST /api/v1/patients/` works the same way (fields: `age`, `gender`, `blood_group`, `address`, `phone`).

## 6. Appointment APIs

`GET/POST /api/v1/appointments/` · `GET/PUT/PATCH/DELETE /api/v1/appointments/{id}/`

Filters: `?doctor=<id>&patient=<id>&status=pending&date=2026-06-20&date_from=2026-06-01&date_to=2026-06-30`

Book an appointment (patient books for themself — `patient` is inferred automatically):
```json
{ "doctor": 1, "appointment_date": "2026-06-25T10:30:00Z" }
```
Admin/receptionist booking on behalf of a patient must include `"patient": <id>`.

Change status (approve/complete/cancel):
`PATCH /api/v1/appointments/{id}/status/` — `{ "status": "approved" }`
(Patients may only set `status` to `cancelled` on their own appointment.)

## 7. Prescription APIs

`POST /api/v1/prescriptions/` — doctors create a prescription with **multiple medicines** in one request:
```json
{
  "appointment": 1,
  "diagnosis": "Acute bronchitis",
  "notes": "Follow up in 1 week if symptoms persist.",
  "medicines": [
    { "medicine": 1, "dosage": "500mg twice a day", "duration": "5 days" },
    { "medicine": 3, "dosage": "1 tablet at night", "duration": "7 days" }
  ]
}
```
`GET /api/v1/prescriptions/` lists prescriptions (scoped by role). `?appointment=<id>` filters by appointment.

## 8. Medicine APIs

`GET /api/v1/medicines/?search=paracetamol` · full CRUD for admin/receptionist.

## 9. Billing APIs

Generate a bill (admin/receptionist):
`POST /api/v1/billing/` — `{ "patient": 1, "amount": "1500.00", "paid": false }`

Mark as paid: `PATCH /api/v1/billing/{id}/mark-paid/` — `{ "paid": true }`

List bills: `GET /api/v1/billing/?patient=<id>&paid=false`

## 10. Error Handling & Validation

- All validation errors return `400` with a consistent shape: `{ "success": false, "errors": {...} }`.
- Permission failures return `403` with a `detail` message.
- Missing/invalid JWT returns `401`.
- Booking a slot that's already taken, double-creating a profile, prescribing without medicines, etc. are all explicitly validated.

## 11. Testing the API

Use Postman, Insomnia, curl, or the built-in DRF Browsable API (visit any
endpoint in your browser while logged in via the admin panel, or attach
the `Authorization: Bearer <token>` header in your client).

Example curl flow:
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "patient_mike", "password": "Patient@123"}'

# Use the returned access token
curl http://127.0.0.1:8000/api/v1/doctors/available/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## 12. ERD Compliance Note

Every model field and relationship matches the provided ERD exactly:
- `User`: username, email, password, first_name, last_name, role, date_joined
- `Doctor`: user (1-1), department (FK), specialization, phone, experience, is_available
- `Patient`: user (1-1), age, gender, blood_group, address, phone
- `Department`: name, description
- `Appointment`: patient (FK), doctor (FK), appointment_date, status, created_at
- `Prescription`: appointment (1-1), diagnosis, notes, created_at
- `PrescriptionMedicine`: prescription (FK), medicine (FK), dosage, duration
- `Medicine`: name, description, unit
- `Bill`: patient (FK), amount, paid, created_at
