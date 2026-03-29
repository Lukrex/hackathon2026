# Setup Guide

This guide covers a full local setup of the current Django application.

## Prerequisites

- Python 3.10+
- pip
- Ability to create a virtual environment
- Optional: Git and VS Code

## 1. Create virtual environment

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Linux or macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Prepare database

```bash
python manage.py migrate
```

Default local database is SQLite (`db.sqlite3`).

## 4. Create admin user

```bash
python manage.py createsuperuser
```

## 5. Load demo data

```bash
python manage.py create_demo_data
```

## 6. Start development server

```bash
python manage.py runserver
```

## Key URLs

- `http://localhost:8000/`
- `http://localhost:8000/accounts/login/`
- `http://localhost:8000/dashboard/`
- `http://localhost:8000/admin/`

## Role model

### Regular user

- Submits requests
- Tracks own requests
- Confirms completion

### Expert

- Maintains profile (skills, languages, availability)
- Works assigned tasks
- Gains karma and help count after confirmed completion

### Worker

- Internal staff role without superuser permissions
- Sees only assigned categories via `WorkerProfile`

### Super-admin

- Sees all requests
- Manages workers and category assignments
- Controls full internal workflow

## API note

DRF viewsets and serializers are present in the codebase, but currently not wired in `server/urls.py` through a router. The web UI is the active execution path.

## Common issues

### Module import errors

Usually the virtual environment is not active. Activate `venv` and run:

```bash
pip install -r requirements.txt
```

### Port already used

```bash
python manage.py runserver 8001
```

### Clean local reset

If you only need a fresh local dev state:

```bash
python manage.py migrate
python manage.py create_demo_data
```
