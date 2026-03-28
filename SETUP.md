# 🚀 Community Help System - Complete Setup Guide

Step-by-step guide to get the Django application running on your system.

## ⚡ Quick Start (5 minutes)

### For Linux/Mac:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python manage.py migrate
python manage.py create_demo_data

# 4. Create admin user
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

Visit: http://localhost:8000/admin/

### For Windows (PowerShell):

```powershell
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python manage.py migrate
python manage.py create_demo_data

# 4. Create admin user
python manage.py createsuperuser

# 5. Run server
python manage.py runserver
```

---

## 📋 Detailed Setup Guide

### Prerequisites

✅ Python 3.8 or higher
✅ pip (comes with Python)
✅ Git (optional, for version control)
✅ 100MB disk space
✅ IDE like VS Code (optional)

### Step 1: Create Python Virtual Environment

**Why?** To isolate project dependencies from system Python

**Linux/Mac:**

```bash
cd hackathon2026
python3 -m venv venv
source venv/bin/activate
```

**Windows (CMD):**

```cmd
cd hackathon2026
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
cd hackathon2026
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Verify activation:** You should see `(venv)` prefix in terminal

---

### Step 2: Install Dependencies

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**What gets installed:**

- Django 4.2.10 (web framework)
- djangorestframework (REST API)
- django-cors-headers (API cross-origin support)
- python-decouple (environment variable management)
- requests (HTTP library)
- pillow (image processing)
- celery (task queue)
- redis (in-memory cache)

**Installation time:** ~2-3 minutes

---

### Step 3: Initialize Database

```bash
# Create database tables
python manage.py migrate

# Load demo data
python manage.py create_demo_data
```

**What happens:**

- SQLite database created at `db.sqlite3`
- All models created (Request, Expert, Category, etc.)
- 7 categories added
- 5 expert profiles created
- 5 sample requests loaded

**Expected output:**

```
✅ Vytvorená kategória: 🔍 Hľadanie zamestnanca
✅ Vytvorený expert: Anna Nováková
...
✅ Demo data vytvorené úspešne!
```

---

### Step 4: Create Admin Account

```bash
python manage.py createsuperuser
```

**Prompts:**

```
Username: admin
Email: admin@example.com
Password: (enter strong password)
Password (again): (confirm)
```

**Save these credentials!** You'll use them to login to the admin panel.

---

### Step 5: Run Development Server

```bash
python manage.py runserver
```

**Expected output:**

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## 🌐 Accessing the System

### Admin Dashboard

📊 http://localhost:8000/admin/

- Login with superuser credentials created above
- Manage requests, experts, categorization
- Manual review and assignment interface

### Submit Request (Public)

📝 http://localhost:8000/submit/

- Public form for request submission
- No login needed
- Receives confirmation email

### API Root

🧠 http://localhost:8000/api/

- REST API for all operations
- JSON responses
- See API_TESTING.md for examples

### Available Endpoints

```
GET    /api/requests/               - List all requests
GET    /api/requests/{id}/          - Single request details
POST   /api/requests/               - Create new request
GET    /api/experts/                - Expert directory
GET    /api/categories/             - Request categories
GET    /api/matches/                - Expert matches
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Edit `.env` to configure:

- DEBUG mode
- Database settings
- Email settings
- Notion API key
- Redis connection

### Email Configuration (Optional)

For development, emails print to console. For production:

1. Edit `server/settings.py`
2. Change EMAIL_BACKEND from 'console' to 'smtp':

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

3. For Gmail: [Create App Password](https://support.google.com/accounts/answer/185833)

### Database Configuration (Optional)

For production, use PostgreSQL instead of SQLite:

1. Install PostgreSQL
2. Create database:
   ```sql
   CREATE DATABASE community_help_db;
   ```
3. Edit `server/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'community_help_db',
           'USER': 'postgres',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
4. Install psycopg2: `pip install psycopg2-binary`
5. Run migrations: `python manage.py migrate`

---

## 🧪 Testing

### Test Admin Interface

1. Go to http://localhost:8000/admin/
2. Login with superuser
3. Click on "Requests"
4. Click on first request
5. Modify priority/category
6. Save changes

### Test API

```bash
# List requests
curl http://localhost:8000/api/requests/

# Create request
curl -X POST http://localhost:8000/api/requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Request",
    "description": "Testing the API",
    "requester_name": "Test User",
    "requester_email": "test@example.com",
    "category": 1
  }'

# See API_TESTING.md for more examples
```

---

## 🔄 Common Operations

### Restart Server (with changes)

```bash
# Press Ctrl+C to stop
# Server auto-reloads on file changes
```

### Reset Database

```bash
# Delete database
rm db.sqlite3

# Recreate with demo data
python manage.py migrate
python manage.py create_demo_data
```

### Create Migrations (after model changes)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Access Django Shell

```bash
python manage.py shell

# In shell:
from server.models import Request, Expert
requests = Request.objects.all()
for r in requests:
    print(r.title)
```

---

## 📦 Using Demo Script

If you prefer an interactive menu:

**Linux/Mac:**

```bash
chmod +x demo.sh
./demo.sh
```

**Windows (Git Bash/WSL):**

```bash
chmod +x demo.sh
./demo.sh
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "db.sqlite3 is locked"

**Solution:**

```bash
# Another process is using the database
# Check for running Django servers
# Kill process: killall python (Linux/Mac)
# Or restart terminal
```

### Issue: Port 8000 already in use

**Solution:**

```bash
# Use different port
python manage.py runserver 8001

# Or kill process using port 8000
# Linux/Mac: lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill
# Windows: netstat -ano | findstr :8000
```

### Issue: Migrations not applying

**Solution:**

```bash
# Check migration status
python manage.py showmigrations

# Apply all migrations
python manage.py migrate

# Create migrations for changes
python manage.py makemigrations
```

### Issue: Emails not sending

**Solution:**

- Development: Emails print to console
- Check Django settings for EMAIL_BACKEND
- For production, configure SMTP settings
- Check email credentials

### Issue: Expert directory empty

**Solution:**

```bash
# Recreate demo data
python manage.py create_demo_data
```

---

## 📚 Next Steps

1. **Explore Admin Interface**
   - Review request management flow
   - Try assigning experts
   - Filter by priority/status

2. **Test API**
   - Use curl or Postman
   - Create requests programmatically
   - See API_TESTING.md for examples

3. **Customize**
   - Add new categories
   - Modify expert matching algorithm
   - Customize email templates

4. **Integrate with Real Systems**
   - Connect Notion API
   - Setup real email backend
   - Connect to your CRM

5. **Deploy**
   - See README.md for production checklist
   - Setup PostgreSQL
   - Configure Celery for task queue

---

## 📞 Support

For issues:

1. Check Troubleshooting section above
2. Review Django documentation: https://docs.djangoproject.com/
3. Check DRF documentation: https://www.django-rest-framework.org/
4. See API_TESTING.md for API-specific help

---

## 🎉 You're All Set!

Your Community Help System is now running!

### Key URLs:

- **Admin:** http://localhost:8000/admin/
- **Submit Request:** http://localhost:8000/submit/
- **API:** http://localhost:8000/api/

**Happy helping! 🤝**

---

_Last updated: March 28, 2026_
_For HalovaMake Hackathon 2026_
