# reelvee – Backend API

REST API for the reelvee platform. Handles authentication (JWT, signup, login, password reset, email verification), user management, and transactional email.

**Stack:** FastAPI · MongoDB (Beanie) · Pydantic · JWT (cookies) · FastAPI-Mail

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Add a `.env` file with MongoDB URI, JWT secret, and SMTP settings (see `app/core/config.py` for required variables).

## Run

```bash
python -m app.main
```

API: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

## Structure

- `app/core` — config, database (Beanie), security, exceptions
- `app/modules/auth` — auth + OTP + tokens
- `app/modules/users` — user CRUD, invitations, update/soft-delete current user
- `app/shared` — schemas, email service, dependencies
