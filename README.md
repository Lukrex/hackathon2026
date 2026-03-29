# zero one hundred Request Coordination Platform

This repository contains a Django application for managing community and company requests from intake to verified completion.

## What the system does

- Lets signed-in users submit structured requests.
- Supports internal triage by admin and worker roles.
- Recommends experts using profile and request signals.
- Tracks request progression with role-based dashboards.
- Supports request-centered and internal chats.
- Allows request creators to confirm completion.
- Updates expert karma and help history on completion.

## Important architecture note

The primary product in this repository is the Django app run via `manage.py`.

There are still legacy Node/Express files in the repo (`package.json`, `server/index.js`, `server/routes/`), but the active web workflow is implemented through Django models, views, forms, and templates.

## Core workflow

1. User submits a request.
2. Internal team reviews and prioritizes it.
3. System proposes expert candidates.
4. Team assigns one or more experts.
5. Work is coordinated through dashboards and chats.
6. Request creator confirms completion.

## Project structure

```text
hackathon2026/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── README.md
├── QUICKSTART.md
├── SETUP.md
├── INDEX.md
├── API_TESTING.md
└── server/
    ├── models.py
    ├── views.py
    ├── viewsets.py
    ├── serializers.py
    ├── forms.py
    ├── tasks.py
    ├── urls.py
    ├── settings.py
    ├── chat_utils.py
    ├── notion_integration.py
    ├── management/commands/create_demo_data.py
    └── templates/
```

## Quick run

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py create_demo_data
python manage.py runserver
```

### Linux or macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py create_demo_data
python manage.py runserver
```

## Main URLs

- Home: `http://localhost:8000/`
- Login: `http://localhost:8000/accounts/login/`
- Register: `http://localhost:8000/register/`
- Submit Request: `http://localhost:8000/submit/`
- Dashboard: `http://localhost:8000/dashboard/`
- Expert Directory: `http://localhost:8000/experts/`
- Django Admin: `http://localhost:8000/admin/`

## Documentation map

- `QUICKSTART.md`: shortest local startup path.
- `SETUP.md`: detailed setup and role behavior.
- `INDEX.md`: where to find what in the codebase.
- `API_TESTING.md`: current API status and testing guidance.
- `INTERNAL_COORDINATION.md`: internal workflow and responsibilities.
