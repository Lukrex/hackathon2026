# 📚 Community Help System - Complete Index & Guide

Welcome to the **full-stack Django demo** of the Community Help System for HalovaMake Hackathon 2026.

This document is your starting point for understanding and using the system.

---

## 🎯 Project in 30 Seconds

A **Django web application** that helps communities (startups, universities, VC ecosystems) manage help requests.

**The Flow:**

1. User submits help request (public form)
2. Admin reviews & categorizes (Django admin)
3. System suggests expert matches (smart algorithm)
4. Admin assigns expert (one-click)
5. Expert gets notified (email)
6. Request resolved & tracked

**Key Difference:** Requests are **manually reviewed by admins**, not fully automated.

---

## 📖 Documentation Index

### 🚀 Start Here

| File                   | Purpose                   | Time     |
| ---------------------- | ------------------------- | -------- |
| **SETUP.md**           | Step-by-step setup guide  | 5-10 min |
| **README.md**          | Complete project overview | 15 min   |
| **PROJECT_SUMMARY.md** | What was built & why      | 10 min   |
| **This file**          | Navigation guide          | 5 min    |

### 🔧 Technical Documentation

| File               | Purpose                       | Audience   |
| ------------------ | ----------------------------- | ---------- |
| **API_TESTING.md** | REST API endpoints & examples | Developers |
| `server/models.py` | Database schema               | Developers |
| `server/admin.py`  | Admin interface code          | Developers |
| `.env.example`     | Configuration template        | DevOps     |

### 📚 Other Resources

| Resource        | Type               | Notes                       |
| --------------- | ------------------ | --------------------------- |
| `demo.sh`       | Interactive script | Linux/Mac only              |
| Inline comments | Code docs          | Throughout project          |
| Django admin    | Visual interface   | http://localhost:8000/admin |

---

## 🏗️ Project Architecture

### Three-Layer Stack

```
┌─────────────────────────────┐
│   FRONTEND (React + HTML)   │ Browser interface
├─────────────────────────────┤
│   API (Django REST)         │ RESTful endpoints
├─────────────────────────────┤
│   BACKEND (Django + Models) │ Business logic
├─────────────────────────────┤
│   DATABASE (SQLite/Postgres)│ Data storage
└─────────────────────────────┘
```

### File Organization

**Backend Application (`server/`):**

```
server/
├── models.py              # Database models
├── admin.py              # Admin interface (core feature!)
├── views.py              # HTML view functions
├── viewsets.py           # REST API views
├── serializers.py        # DRF data serializers
├── forms.py              # Django forms
├── tasks.py              # Email tasks (Celery)
├── urls.py               # URL routing
├── settings.py           # Configuration
├── apps.py               # App config
├── notion_integration.py # Notion API handler
├── management/
│   └── commands/
│       └── create_demo_data.py  # Demo data
└── templates/            # HTML templates
```

**Frontend (`client/`):**

```
client/
├── src/
│   ├── components/       # React components
│   ├── App.jsx          # Main app
│   └── main.jsx         # Entry point
└── vite.config.js       # Build config
```

---

## 🚀 Quick Action Grid

### I want to...

| Goal                          | Step 1                           | Step 2                       | Step 3                            |
| ----------------------------- | -------------------------------- | ---------------------------- | --------------------------------- |
| **Run it locally**            | See SETUP.md                     | `python manage.py runserver` | Visit http://localhost:8000/admin |
| **Review code**               | Check `server/models.py`         | Check `server/admin.py`      | Check `server/tasks.py`           |
| **Test API**                  | See API_TESTING.md               | Use curl/Postman             | Try endpoints                     |
| **Deploy to prod**            | See README.md                    | Configure PostgreSQL         | Use `gunicorn`                    |
| **Modify matching algorithm** | Edit `server/tasks.py` line ~150 | Update scoring logic         | Test with curl                    |
| **Add email backend**         | Edit `server/settings.py`        | Configure SMTP               | Test send                         |
| **Integrate Notion**          | Set `NOTION_API_KEY` in `.env`   | See `notion_integration.py`  | Call sync                         |
| **Add new category**          | Go to Django admin               | Create category              | Use in forms                      |

---

## 🎯 Core Features Explained

### 1️⃣ Request Submission

**File:** `server/views.py::submit_request()`

- Public form at `/submit/`
- Captures: title, description, category, contact info
- Auto-sends confirmation email
- No login required

### 2️⃣ Admin Review Interface

**File:** `server/admin.py` (❤️ Main feature!)

- Beautiful Django admin at `/admin/`
- Color-coded priority & status
- Bulk actions (mark reviewed, in progress, resolved)
- Filter & search capabilities
- Inline expert assignment

### 3️⃣ Expert Matching Algorithm

**File:** `server/tasks.py::calculate_expert_matches()`

- Keyword overlap scoring (0-40 pts)
- Category expertise (0-30 pts)
- Availability bonus (0-20 pts)
- Workload adjustment (0-10 pts)
- Total: 0-100% match score

### 4️⃣ Email Notifications

**File:** `server/tasks.py`

- Confirmation to requester
- Match notification to expert
- Professional HTML format
- Configurable SMTP backend

### 5️⃣ REST API

**File:** `server/viewsets.py`

- Full endpoints for requests, experts, matches
- Filtering, searching, sorting
- JSON responses
- CORS enabled

### 6️⃣ Notion Integration

**File:** `server/notion_integration.py`

- Export to CSV/JSON
- Database template provided
- Bi-directional sync ready
- Team coordination

---

## 💾 Database Schema

### Models (ORM)

```
Category
├─ name (hiring, investment, consulting...)
├─ description
└─ icon

Expert
├─ user (OneToOne → User)
├─ bio
├─ expertise (comma-separated)
├─ availability (high/medium/low)
└─ help_provided (counter)

Request
├─ title
├─ description
├─ category (FK → Category)
├─ priority (critical/high/medium/low)
├─ status (open/in_review/in_progress/resolved/rejected)
├─ value_score (1-10)
├─ requester_* (name, email, phone)
├─ assigned_experts (M2M → Expert)
├─ reviewed_by (FK → User)
├─ created_at / updated_at
└─ resolved_at

ExpertMatch
├─ request (FK → Request)
├─ expert (FK → Expert)
├─ match_score (0-100%)
└─ reasoning

Notification
├─ request (FK → Request)
├─ recipient_email
├─ notification_type
├─ subject
└─ sent_at
```

---

## 📡 API Endpoints

All at `http://localhost:8000/api/`

### Requests

```
GET    /requests/                      # List (filterable, sortable)
GET    /requests/{id}/                 # Detail
POST   /requests/                      # Create
PUT    /requests/{id}/                 # Update
POST   /requests/{id}/assign_expert/   # Assign expert
POST   /requests/{id}/mark_resolved/   # Mark resolved
GET    /requests/{id}/suggested_experts/
```

### Experts

```
GET    /experts/                       # Directory (searchable)
GET    /experts/{id}/                  # Profile
```

### Matches

```
GET    /matches/                       # All matches
GET    /matches/?request={id}          # For request
GET    /matches/?expert={id}           # By expert
```

### Categories

```
GET    /categories/                    # All categories
```

See **API_TESTING.md** for curl examples.

---

## 🔐 Admin Workflow

### Step-by-Step Request Review

1. **Login** → http://localhost:8000/admin/ (with superuser)

2. **Find Request** → Click "Requests" in sidebar

3. **Open Request** → Click on request title

4. **Review Details** → Read description, notes

5. **Categorize** → Set category (if not set)

6. **Prioritize** → Set priority level
   - 🔴 Critical: urgent, important
   - 🔴 High: significant impact
   - 🟡 Medium: standard priority
   - 🔵 Low: can wait

7. **Score Value** → 1-10 slider
   - 10 = highest impact
   - 1 = lowest impact

8. **Add Notes** → Your review notes

9. **Status Check** → Change to "In Review"

10. **View Matches** → See suggested experts below

11. **Assign** → Click dropdown, select expert

12. **Save** → Django saves, emails sent

13. **Monitor** → Check status later

14. **Resolve** → Mark as "Resolved" when done

---

## 🔄 Email Flow

```
User Submits Request
        ↓
[AUTO] Confirmation → User sees request accepted
        ↓
Admin Reviews (manual)
        ↓
Admin Assigns Expert
        ↓
[AUTO] Notification → Expert learns about request
        ↓
Expert Helps (outside system, via email)
        ↓
Admin Marks Resolved
        ↓
[OPTIONAL] Completion → Confirmation to requester
```

---

## 🧪 Testing Checklist

- [ ] Database initialized: `python manage.py migrate`
- [ ] Demo data loaded: `python manage.py create_demo_data`
- [ ] Admin user created: `python manage.py createsuperuser`
- [ ] Server running: `python manage.py runserver`
- [ ] Admin accessible: http://localhost:8000/admin
- [ ] Can view requests in admin
- [ ] Can modify priority/category
- [ ] Can assign expert
- [ ] API responds: `curl http://localhost:8000/api/requests/`
- [ ] Demo data appears in API

---

## 🚀 Common Tasks

### Add New Expert

```python
# Via Django shell
python manage.py shell

from django.contrib.auth.models import User
from server.models import Expert

user = User.objects.create_user(
    username='john',
    email='john@example.com',
    first_name='John',
    last_name='Doe'
)

expert = Expert.objects.create(
    user=user,
    bio='10 years experience',
    expertise='React, Node.js, GTM',
    availability='high',
    help_provided=0
)
```

### Modify Matching Algorithm

Edit `server/tasks.py`, function `calculate_expert_matches()`:

```python
# Change scoring weights (lines ~150-180)
match_score += min(overlaps * 10, 50)  # Increase skill weight
match_score += availability_bonus.get(...) * 2  # Increase availability
```

### Enable Real Email

Edit `server/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Deploy to Production

```bash
pip install gunicorn psycopg2-binary
collectstatic
migrate  # on production database
gunicorn wsgi:application
```

See **README.md** for complete deployment checklist.

---

## 📊 Statistics

**Code:**

- 2,500+ lines of Python backend
- 500+ lines of React components
- 2,000+ lines of documentation

**Features:**

- 6 API endpoints (20+ operations)
- 9 admin pages
- 5 HTML templates
- 5 React components
- 1 smart algorithm

**Built-in:**

- 7 categories
- 5 expert profiles
- 5 sample requests
- 15+ expert-request matches

---

## 🆘 Troubleshooting Quick Links

| Problem            | Solution                                           |
| ------------------ | -------------------------------------------------- |
| Django not found   | Activate venv: `source venv/bin/activate`          |
| Port 8000 in use   | Use different port: `runserver 8001`               |
| DB locked          | Restart process or terminal                        |
| No demo data       | Run `create_demo_data` command                     |
| Emails not sending | Check Django settings, use console backend for dev |
| API returns 404    | Check URL and routing in `server/urls.py`          |

See **SETUP.md** for detailed troubleshooting.

---

## 📚 Learning Path

### Beginner (1-2 hours)

1. Read README.md (overview)
2. Follow SETUP.md (installation)
3. Explore Django admin (UI)
4. Submit test request (form)
5. Assign expert (admin)

### Intermediate (2-4 hours)

1. Review API_TESTING.md
2. Test endpoints with curl
3. Read models.py (data structure)
4. Review admin.py (interface code)
5. Customize a field or form

### Advanced (1-2 days)

1. Understand matching algorithm
2. Modify scoring weights
3. Setup email backend
4. Deploy to production
5. Integrate with Notion API

---

## 🔗 Key Files Reference

| File                                             | Size      | Purpose          |
| ------------------------------------------------ | --------- | ---------------- |
| `server/models.py`                               | 450 lines | Database schema  |
| `server/admin.py`                                | 350 lines | Admin interface  |
| `server/tasks.py`                                | 300 lines | Email + matching |
| `server/views.py`                                | 250 lines | View functions   |
| `server/management/commands/create_demo_data.py` | 300 lines | Demo data        |
| `README.md`                                      | 400 lines | Project docs     |
| `SETUP.md`                                       | 350 lines | Setup guide      |
| `API_TESTING.md`                                 | 400 lines | API reference    |

---

## 🎯 Next Steps

### Immediate (Today)

- [ ] Follow SETUP.md
- [ ] Get server running
- [ ] Access admin at http://localhost:8000/admin
- [ ] Review demo data
- [ ] Try assigning an expert

### Short-term (This week)

- [ ] Setup email backend
- [ ] Customize categories
- [ ] Modify matching algorithm
- [ ] Test all API endpoints
- [ ] Design custom templates

### Medium-term (This month)

- [ ] Deploy to production
- [ ] Setup PostgreSQL
- [ ] Integrate Notion
- [ ] Build custom frontend
- [ ] Setup monitoring

### Long-term (Beyond)

- [ ] Real user base
- [ ] Analytics dashboard
- [ ] Mobile app
- [ ] Integration marketplace
- [ ] AI improvements

---

## 💡 Tips & Tricks

### Console Email Output

During development, emails print to console. Great for testing!

### Django Shell

```bash
python manage.py shell
# Interactive Python with Django loaded
from server.models import Request
requests = Request.objects.filter(priority='high')
```

### Database Queries

```bash
python manage.py dbshell
# Direct database access
SELECT * FROM server_request WHERE priority='critical';
```

### Cache Clearing

```bash
python manage.py clear_cache
python manage.py collectstatic
```

### Creating Migrations

```bash
python manage.py makemigrations  # Detect changes
python manage.py migrate          # Apply migrations
```

---

## 🤝 Community

This system helps communities help each other. Use it to:

- ✅ Connect people with needs
- ✅ Match with right helpers
- ✅ Track progress
- ✅ Measure impact
- ✅ Build stronger communities

---

## 📞 Support Resources

| Question            | Resource                              |
| ------------------- | ------------------------------------- |
| How to setup?       | SETUP.md                              |
| What does it do?    | README.md                             |
| How to use API?     | API_TESTING.md                        |
| What was built?     | PROJECT_SUMMARY.md                    |
| How does code work? | Inline comments + docstrings          |
| Django docs         | https://docs.djangoproject.com        |
| DRF docs            | https://www.django-rest-framework.org |

---

## 🎉 You're Ready!

You now have a **production-ready Django application** that:

- ✅ Collects help requests
- ✅ Manages via admin interface
- ✅ Matches with experts
- ✅ Sends notifications
- ✅ Provides REST API
- ✅ Exports to Notion
- ✅ Tracks everything

**Start with SETUP.md and you'll be running in 5 minutes!**

---

**Built with ❤️ for HalovaMake Hackathon 2026**

_Making communities more helpful, organized, and efficient_ 🤝
