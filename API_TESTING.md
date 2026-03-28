# 📋 API Testing Guide - Community Help System

Complete guide for testing all API endpoints with curl examples.

## 🚀 Getting Started

### Server Status
```bash
curl http://localhost:8000/health/
# Response: {"status":"ok"}
```

### API Root
```bash
curl http://localhost:8000/api/
# Lists all available API endpoints
```

---

## 📝 Requests API

### 1. List All Requests
```bash
curl "http://localhost:8000/api/requests/"

# With filtering
curl "http://localhost:8000/api/requests/?status=open&priority=high"

# With search
curl "http://localhost:8000/api/requests/?search=React+developer"

# With sorting
curl "http://localhost:8000/api/requests/?ordering=-created_at"
```

**Query Parameters:**
- `status`: `open`, `in_review`, `waiting_expert`, `in_progress`, `resolved`, `rejected`
- `priority`: `low`, `medium`, `high`, `critical`
- `category`: Category ID (see Categories API)
- `search`: Full-text search in title/description
- `ordering`: `-created_at`, `-priority`, `-value_score`
- `page`: Page number (pagination)

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Need React Developer",
      "requester_name": "John Doe",
      "category": 1,
      "category_display": "🔍 Hľadanie zamestnanca",
      "priority": "high",
      "priority_display": "🔴 Vysoká",
      "status": "in_review",
      "status_display": "🟡 V preverovaní",
      "value_score": 9,
      "expert_count": 2,
      "created_at": "2024-03-20T10:30:00Z"
    }
  ]
}
```

---

### 2. Get Single Request Details
```bash
curl "http://localhost:8000/api/requests/1/"
```

**Response:**
```json
{
  "id": 1,
  "title": "Need React Developer",
  "description": "Looking for senior React developer with 5+ years experience...",
  "requester_name": "John Doe",
  "requester_email": "john@example.com",
  "requester_phone": "+421123456789",
  "category": 1,
  "category_display": "🔍 Hľadanie zamestnanca",
  "priority": "high",
  "priority_display": "🔴 Vysoká",
  "status": "in_progress",
  "status_display": "🟠 V riešení",
  "value_score": 9,
  "review_notes": "Good candidate for senior role",
  "assigned_experts": [
    {
      "id": 1,
      "full_name": "Anna Nováková",
      "bio": "10+ years in startups...",
      "expertise": "React, Node.js, GTM",
      "expertise_list": ["React", "Node.js", "GTM"],
      "availability": "high",
      "help_provided": 8,
      "profile_image": null
    }
  ],
  "suggested_matches": [
    {
      "id": 5,
      "expert": 2,
      "expert_detail": {...},
      "match_score": 85.5,
      "reasoning": "High keyword overlap, availability match",
      "created_at": "2024-03-20T11:00:00Z"
    }
  ],
  "created_at": "2024-03-20T10:30:00Z",
  "updated_at": "2024-03-20T11:30:00Z",
  "resolved_at": null,
  "resolution_notes": "",
  "reviewer_name": "admin"
}
```

---

### 3. Create New Request
```bash
curl -X POST "http://localhost:8000/api/requests/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Seeking Node.js Expert",
    "description": "We need help building scalable Node.js backend for our SaaS",
    "requester_name": "Jane Smith",
    "requester_email": "jane@startup.com",
    "requester_phone": "+421987654321",
    "category": 1
  }'
```

**Response:** (HTTP 201 Created)
```json
{
  "id": 6,
  "title": "Seeking Node.js Expert",
  "description": "We need help building scalable Node.js backend...",
  "requester_name": "Jane Smith",
  "requester_email": "jane@startup.com",
  "requester_phone": "+421987654321",
  "category": 1,
  "status": "open"
}
```

---

### 4. Update Request (Admin)
```bash
curl -X PUT "http://localhost:8000/api/requests/1/" \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "critical",
    "value_score": 10,
    "review_notes": "Very important for company success",
    "status": "in_progress"
  }'
```

---

### 5. Assign Expert to Request
```bash
curl -X POST "http://localhost:8000/api/requests/1/assign_expert/" \
  -H "Content-Type: application/json" \
  -d '{
    "expert_id": 2
  }'

# Response:
# {
#   "status": "success",
#   "message": "Expert Anna Nováková assigned to request"
# }
```

**Effect:** Expert gets email notification about the match

---

### 6. Mark Request as Resolved
```bash
curl -X POST "http://localhost:8000/api/requests/1/mark_resolved/" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Successfully hired 2 developers through our expert'snetwork"
  }'

# Response:
# {
#   "status": "success",
#   "message": "Request marked as resolved"
# }
```

---

### 7. Get Suggested Experts for Request
```bash
curl "http://localhost:8000/api/requests/1/suggested_experts/"

# Response: [list of ExpertMatch objects with scores]
```

---

## 👥 Experts API

### 1. List All Experts
```bash
curl "http://localhost:8000/api/experts/"

# Filter by availability
curl "http://localhost:8000/api/experts/?availability=high"

# Search by name or expertise
curl "http://localhost:8000/api/experts/?search=React"

# Sort by help provided
curl "http://localhost:8000/api/experts/?ordering=-help_provided"
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "full_name": "Anna Nováková",
      "bio": "10+ years in startups...",
      "expertise": "React, Node.js, GTM, Scaling",
      "expertise_list": ["React", "Node.js", "GTM", "Scaling"],
      "availability": "high",
      "help_provided": 8,
      "profile_image": null
    }
  ]
}
```

---

### 2. Get Single Expert Profile
```bash
curl "http://localhost:8000/api/experts/1/"

# Response:
# {
#   "id": 1,
#   "full_name": "Anna Nováková",
#   "bio": "...",
#   "expertise": "...",
#   ...
# }
```

---

## 🔗 Expert Matches API

### 1. List All Matches
```bash
curl "http://localhost:8000/api/matches/"

# Filter by request
curl "http://localhost:8000/api/matches/?request=1"

# Filter by expert
curl "http://localhost:8000/api/matches/?expert=2"

# Sort by score
curl "http://localhost:8000/api/matches/?ordering=-match_score"
```

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 5,
      "expert": 1,
      "expert_detail": {
        "id": 1,
        "full_name": "Anna Nováková",
        ...
      },
      "match_score": 87.5,
      "reasoning": "High expertise overlap (React, Node.js), high availability",
      "created_at": "2024-03-20T11:00:00Z"
    }
  ]
}
```

---

## 🏷️ Categories API

### 1. List All Categories
```bash
curl "http://localhost:8000/api/categories/"

# Response:
{
  "count": 7,
  "results": [
    {
      "id": 1,
      "name": "hiring",
      "description": "Finding employees and talent",
      "icon": "🔍"
    },
    {
      "id": 2,
      "name": "investment",
      "description": "Finding investors and capital",
      "icon": "💰"
    }
    ...
  ]
}
```

---

## 🔧 Usage Examples

### Example 1: Submit Request → Get Matches → Assign Expert

```bash
# 1. Submit request
REQUEST_ID=$(curl -s -X POST "http://localhost:8000/api/requests/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Seeking Marketing Expert",
    "description": "Need help with digital marketing strategy",
    "requester_name": "Test User",
    "requester_email": "test@example.com",
    "category": 4
  }' | jq -r '.id')

echo "Created request: $REQUEST_ID"

# 2. Get suggested matches (after admin review)
sleep 2
curl "http://localhost:8000/api/requests/$REQUEST_ID/suggested_experts/" | jq

# 3. Assign top expert
EXPERT_ID=$(curl -s "http://localhost:8000/api/requests/$REQUEST_ID/suggested_experts/" | \
  jq -r '.[0].expert')

curl -X POST "http://localhost:8000/api/requests/$REQUEST_ID/assign_expert/" \
  -H "Content-Type: application/json" \
  -d "{\"expert_id\": $EXPERT_ID}"
```

---

### Example 2: Find All High-Priority Open Requests

```bash
curl "http://localhost:8000/api/requests/?status=open&priority=high" | jq '.results[] | {id, title, requester_name}'
```

---

### Example 3: Get Expert Statistics

```bash
curl "http://localhost:8000/api/experts/" | jq '.results | map({name: .full_name, help_provided, availability})'
```

---

## 📊 Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Successful GET/PUT/PATCH |
| 201 | Created - POST successful |
| 400 | Bad Request - Invalid data |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error |

---

## 🔐 Authentication

The demo API doesn't require authentication. For production, add token auth:

```bash
# Get token
curl -X POST "http://localhost:8000/api-token-auth/" \
  -d "username=admin&password=password"

# Use token
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  "http://localhost:8000/api/requests/"
```

---

## 📥 Import/Export

### Export to CSV
```bash
curl "http://localhost:8000/api/requests/?format=csv" > requests.csv
```

### Export to JSON
```bash
curl "http://localhost:8000/api/requests/?format=json" > requests.json
```

---

## 🐍 Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api"

# List requests
response = requests.get(f"{BASE_URL}/requests/")
requests_data = response.json()

# Create request
new_request = {
    "title": "Need DevOps Engineer",
    "description": "Help setting up CI/CD pipeline",
    "requester_name": "Bob",
    "requester_email": "bob@company.com",
    "category": 1
}
response = requests.post(f"{BASE_URL}/requests/", json=new_request)
request_id = response.json()['id']

# Get matches
response = requests.get(f"{BASE_URL}/requests/{request_id}/suggested_experts/")
matches = response.json()

# Assign expert
expert_id = matches[0]['expert']
response = requests.post(
    f"{BASE_URL}/requests/{request_id}/assign_expert/",
    json={"expert_id": expert_id}
)
```

---

## 🧪 Testing with Postman

1. Import the API URL into Postman
2. Create requests for each endpoint
3. Save as Postman Collection for team sharing

---

## 📝 Notes

- Emails are printed to console in development mode
- To test email, configure SMTP in settings.py
- Celery tasks run asynchronously (set up Redis)
- Pagination returns 20 items per page by default

---

**Happy testing! 🚀**
