# reelvee – Backend API

REST API for the reelvee platform written in FastAPI..

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

## Docs

You can find Swagger docs on `http://{host}:{port}/docs`. Also it's available on `http://{host}:{port}/redoc`

## Structure

- `app/core` — config, database (Beanie), security, exceptions
- `app/modules/auth` — auth + OTP + tokens
- `app/modules/users` — user CRUD, profile change
- `app/shared` — schemas, email service, dependencies
