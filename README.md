# 🤝 Community Help System - Django Full Stack Demo

A comprehensive digital platform for managing community help requests, matching experts, and prioritizing needs. Built with **Django** backend, featuring **manual admin review** of requests, smart expert matchmaking, and Notion integration.

## 📊 System Overview

This system solves the challenge of **organizing community help** in startups, universities, and VC ecosystems by:

- **Collecting** structured help requests from community members
- **Reviewing** and categorizing requests manually through a beautiful admin interface
- **Matching** requests with appropriate experts using intelligent scoring
- **Coordinating** help delivery with email notifications and tracking
- **Integrating** with Notion for team coordination

## 🎯 Key Features

### 1. **Request Submission** 📝

- Public form for anyone to submit help requests
- Structured data collection (title, description, category, contact info)
- Automatic confirmation emails to requesters
- Support categories:
  - 🔍 Hiring (finding employees/talent)
  - 💰 Investment (finding capital/investors)
  - 📊 Consulting (expert advice & strategy)
  - 📢 Marketing (marketing materials & campaigns)
  - 🎤 Speaking (event speaking opportunities)
  - 🤝 Networking (community connections)
  - 💼 Sales (sales support & training)

### 2. **Manual Admin Review** 🔍

- Beautiful Django admin interface for request review
- Admins manually categorize and prioritize requests
- Set priority levels (Critical, High, Medium, Low)
- Add review notes and assign experts
- Track request status: Open → In Review → In Progress → Resolved
- Bulk actions for quick categorization

### 3. **Smart Expert Matching** 🧠

- AI-style scoring algorithm for expert-request matching
- Matches based on:
  - Expertise overlap (0-40 points)
  - Category fit (0-30 points)
  - Availability (0-20 points)
  - Current workload (0-10 points)
- Visual match scoring (0-100%)
- Suggest top-ranked experts for each request

### 4. **Expert Directory** 👥

- Complete expert profiles with bio and expertise
- Track help provided statistics
- Availability levels (High, Medium, Low)
- Search and filter by expertise and availability
- Expert management through admin panel

### 5. **Request Tracking** 📊

- Dashboard with real-time statistics
- Request status tracking
- Category distribution analytics
- Priority filtering
- Resolved vs. open request monitoring

### 6. **Email Integration** 📧

- Automatic confirmation emails to requesters
- Expert match notifications
- Status update notifications
- HTML-formatted professional emails
- Track all sent notifications

### 7. **Notion Integration** 🔄

- Export requests and experts to CSV/JSON
- Notion database template included
- Bi-directional sync capability (when API key configured)
- Keep team informed in Notion workspace

## 🏗️ Architecture

- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: REST endpoints for all operations
- **Admin**: Full-featured Django admin interface
- **Tasks**: Celery for async email sending (optional)
- **Frontend**: React/React admin dashboards (included)

## 📦 Project Structure

```
hackathon2026/
├── manage.py                           # Django management script
├── requirements.txt                    # Python dependencies
├── README.md                          # This file
├── API_TESTING.md                     # API documentation
├── server/                            # Main Django app
│   ├── __init__.py
│   ├── admin.py                       # Admin interface configuration
│   ├── apps.py
│   ├── models.py                      # Database models
│   ├── views.py                       # View functions
│   ├── viewsets.py                    # API ViewSets
│   ├── serializers.py                 # REST serializers
│   ├── forms.py                       # Django forms
│   ├── tasks.py                       # Celery tasks
│   ├── settings.py                    # Django settings
│   ├── urls.py                        # URL routing
│   ├── notion_integration.py          # Notion API
│   ├── templates/                     # HTML templates
│   │   ├── submit_request.html
│   │   ├── dashboard.html
│   │   ├── review_request.html
│   │   ├── expert_directory.html
│   │   └── request_detail.html
│   └── management/commands/
│       └── create_demo_data.py        # Demo data generator
├── client/                            # React frontend (optional)
│   └── src/
│       └── components/
│           └── ExpertProfiles.jsx
└── db.sqlite3                         # Development database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Optional: Redis (for Celery tasks)
- Optional: PostgreSQL (for production)

### Installation

1. **Clone and navigate**

```bash
cd hackathon2026
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create superuser (admin account)**

```bash
python manage.py migrate                 # Create database
python manage.py createsuperuser        # Create admin account
```

5. **Load demo data**

```bash
python manage.py create_demo_data       # Load sample requests and experts
```

6. **Run development server**

```bash
python manage.py runserver              # Server on http://localhost:8000
```

7. **Access the system**

- 📊 Admin Dashboard: http://localhost:8000/admin/
- 📝 Submit Request: http://localhost:8000/submit/
- 🧠 API Root: http://localhost:8000/api/
- 📋 Requests API: http://localhost:8000/api/requests/
- 👥 Experts API: http://localhost:8000/api/experts/

## 🎮 Using the System

### For Request Submitters

1. Go to **Submit Request** page
2. Fill in the form with:
   - Title: What you need
   - Description: Detailed explanation
   - Category: Pick relevant area
   - Contact info: Email and phone
3. Submit and you'll receive a confirmation email
4. Wait for expert matches (admin will assign them)

### For Admin (Manual Review)

1. Go to **Django Admin** (http://localhost:8000/admin/)
2. Navigate to **Requests**
3. Click on a request with status "🟢 Open"
4. Review the request details
5. Manually set:
   - Category (if not set)
   - Priority level
   - Value score (1-10)
   - Review notes
6. Click "Mark as In Review" action
7. System will calculate expert matches
8. Assign top-matched experts
9. Change status to "In Progress"
10. When resolved, mark as "Resolved"

### API Endpoints

**Requests**

```
GET    /api/requests/               # List all requests (sortable, filterable)
GET    /api/requests/{id}/          # Get single request
POST   /api/requests/               # Create new request
PUT    /api/requests/{id}/          # Update request
POST   /api/requests/{id}/assign_expert/    # Assign expert
POST   /api/requests/{id}/mark_resolved/    # Mark resolved
```

**Experts**

```
GET    /api/experts/                # List all experts
GET    /api/experts/{id}/           # Get expert profile
```

**Matchmaking**

```
GET    /api/matches/                # List all matches
GET    /api/matches?request={id}    # Get matches for request
```

**Categories**

```
GET    /api/categories/             # List all categories
```

## 📧 Email Configuration

By default, emails are printed to console for development.

### Production Email Setup

Edit `server/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

## 🔗 Notion Integration

### Setup

1. Create Notion integration at https://www.notion.so/my-integrations
2. Create a database with template structure
3. Add to `.env`:

```
NOTION_API_KEY=your_api_key_here
NOTION_DATABASE_ID=your_database_id_here
```

4. Use API to sync:

```python
from server.notion_integration import NotionIntegrator
from server.models import Request

notioner = NotionIntegrator()
notioner.sync_requests_to_notion(Request.objects.all())
```

### CSV Export

Get CSV-compatible data via API:

```
GET /api/requests/?format=csv
```

Import to Notion using "Create database from CSV" feature.

## 🧪 Testing API

See **API_TESTING.md** for complete API testing guide with curl examples.

Quick test:

```bash
# List all requests
curl http://localhost:8000/api/requests/

# Create request via API
curl -X POST http://localhost:8000/api/requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Need React Developer",
    "description": "Looking for senior React developer",
    "requester_name": "John Doe",
    "requester_email": "john@example.com",
    "category": 1
  }'
```

## 📊 Demo Data

The system comes pre-loaded with:

- ✅ 7 request categories
- ✅ 5 expert profiles
- ✅ 5 sample requests
- ✅ Expert match suggestions
- ✅ Various request statuses

Run `python manage.py create_demo_data` anytime to reset demo data.

## 🔐 Security

- CSRF protection enabled (Django templates)
- SQL injection protected (ORM)
- XSS protection (template escaping)
- Admin login required for sensitive operations
- Email validation on submission

## 🚀 Production Deployment

### Database Setup

```bash
# Use PostgreSQL in production
pip install psycopg2-binary
```

Edit `settings.py`:

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

### Celery Task Queue (optional)

```bash
# Install Redis
# Then run Celery worker
celery -A server worker -l info
```

### Deploy Checklist

- [ ] Set `DEBUG = False`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure allowed hosts
- [ ] Setup email backend
- [ ] Configure Notion integration
- [ ] Setup PostgreSQL
- [ ] Setup Redis for Celery
- [ ] Configure static files
- [ ] Setup HTTPS/SSL
- [ ] Run migrations on production

```bash
python manage.py collectstatic
python manage.py migrate
gunicorn server.wsgi
```

## 💡 Key Design Decisions

1. **Manual Review**: Requests are manually reviewed by admins, not fully automated, to ensure quality and accuracy
2. **Expert Matching**: Intelligent scoring algorithm considers multiple factors (skills, availability, workload)
3. **Email-First**: All communications happen via email for transparency and async operation
4. **REST API**: Full API for frontend integration and external systems
5. **Django Admin**: Leverage Django's built-in admin for rapid development

## 🎓 Customization

### Add New Request Categories

```python
# In Django shell
from server.models import Category
Category.objects.create(
    name='custom',
    description='Custom category',
    icon='🆕'
)
```

### Customize Expert Matching

Edit the `calculate_expert_matches` function in `server/tasks.py` to adjust scoring weights.

### Add Custom Fields

Add to `Request` model in `models.py`, run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 📝 License

Created for **HalovaMake Hackathon 2026**

---

**Made with ❤️ by the Community Help System Team**
