# Quickstart

Use this file for the fastest local setup.

## 1. Create and activate virtual environment

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux or macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Initialize database and demo data

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_demo_data
```

## 4. Run server

```bash
python manage.py runserver
```

## 5. Open app

- Home: `http://localhost:8000/`
- Login: `http://localhost:8000/accounts/login/`
- Dashboard: `http://localhost:8000/dashboard/`
- Admin: `http://localhost:8000/admin/`

## Quick verification checklist

- You can log in with your superuser account.
- Dashboard loads with request and expert sections.
- Expert directory shows data.
- New requests can be submitted.

## Troubleshooting

- Missing package errors: make sure `venv` is activated, then run `pip install -r requirements.txt`.
- Port 8000 busy: run `python manage.py runserver 8001`.
- Local DB reset (development only): delete `db.sqlite3`, then rerun migrations and demo data.
