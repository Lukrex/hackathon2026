# 🚀 Community Help System - QUICK START GUIDE

## Project Overview
A complete demo system for managing community help requests with intelligent expert matchmaking, automatic categorization, and integrations.

## 📦 What's Included

✅ **Backend (Node.js + Express)**
- 4 core API modules (requests, matchmaking, email, notion)
- Smart categorization algorithm
- Intelligent prioritization system
- Expert matching algorithm
- Email notifications
- Notion integration

✅ **Frontend (React + Vite)**
- Beautiful dashboard with metrics
- Request listing and management
- Expert matchmaking interface
- Expert directory
- New request form

✅ **Demo Data**
- 5 sample requests
- 5 community experts
- Pre-configured categories and expertise areas

## 🎯 Start Here (3 Steps)

### Step 1: Install Dependencies
```bash
npm install
cd client && npm install && cd ..
```

### Step 2: Start Backend
```bash
npm run server:dev
```
✅ Backend running on http://localhost:3001

### Step 3: Start Frontend (new terminal)
```bash
npm run client:dev
```
✅ Frontend running on http://localhost:3000

## 🎨 UI Overview

### Dashboard View
- **Metrics**: Open requests, in progress, resolved
- **Categories**: Visual breakdown by type
- **Analytics**: Total value and expert engagement

### Requests List
- Sort by priority or recent
- View all requests with details
- Quick matchmaking access
- Status tracking

### Expert Finder
- Find experts by category
- View expertise and availability
- One-click assignment
- Contact information

### Create Request
- Simple form submission
- Auto-categorization
- Auto-prioritization
- Instant expert matching

## 🧪 Test Features

### 1. View Demo Data
1. Open http://localhost:3000
2. Click "📊 Dashboard" - see metrics
3. Click "📋 Žiadosti" - see all requests

### 2. Create New Request
1. Click "➕ Nová žiadosť"
2. Fill in details
3. Submit
4. Watch it get categorized and matched!

### 3. Test Matchmaking
1. Click request in table
2. See expert recommendations
3. Click "✓ Priradiť" to assign
4. Expert gets assigned + email notification

### 4. View Experts
1. Click "👥 Experty"
2. Browse all experts
3. See expertise and stats
4. Contact directly

## 📡 API Testing

### Get all requests
```bash
curl http://localhost:3001/api/requests
```

### Create new request
```bash
curl -X POST http://localhost:3001/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hľadáme frontend developer",
    "description": "Skúsený React developer...",
    "requester": {"id": "u1", "name": "MyStartup", "email": "hi@startup.sk"},
    "tags": ["react", "remote"]
  }'
```

### Get expert matches
```bash
curl http://localhost:3001/api/matchmaking/request/req-001
```

### Assign expert
```bash
curl -X POST http://localhost:3001/api/matchmaking/assign \
  -H "Content-Type: application/json" \
  -d '{"requestId": "req-001", "expertId": "expert-1"}'
```

See `API_TESTING.md` for complete API documentation.

## 🔧 Tech Stack

**Backend**
- Node.js
- Express.js
- CORS
- Nodemailer (email)

**Frontend**
- React 18
- Vite (build tool)
- Axios (HTTP client)
- CSS3 (styling)

**Database**
- In-memory (demo mode)
- Ready for PostgreSQL/MongoDB

## 🎯 Key Algorithms

### Categorization
Keywords-based detection:
- **hiring**: developer, programmer, react, python
- **investment**: funding, VC, investor, seed
- **consulting**: strategy, GTM, advise
- **marketing**: copywriting, content, SEO
- **speaking**: event, speaker, conference

### Prioritization
Scoring based on:
- Recency (newer = higher)
- Status (open > in_progress)
- Engagement (less help = higher)
- Keywords (urgent, critical)

### Matchmaking
Score calculation:
- Category match: +5 points
- Keywords overlap: +1 per keyword
- Availability: high=3, medium=1, low=0
- Workload: less busy + points

## 📊 Demo Data

**Requests:**
| ID | Title | Category | Priority | Status |
|---|---|---|---|---|
| req-001 | React developer | hiring | high | open |
| req-002 | VC funding | investment | high | open |
| req-003 | GTM strategy | consulting | medium | open |
| req-004 | Tech speaker | speaking | low | open |
| req-005 | Copywriting | marketing | medium | in_progress |

**Experts:**
| ID | Name | Expertise | Availability | Help Provided |
|---|---|---|---|---|
| expert-1 | Peter Kováč | hiring, recruitment | high | 8 |
| expert-2 | Jana Novotná | investment, finance | medium | 12 |
| expert-3 | Marko Szabó | marketing, gtm | high | 6 |
| expert-4 | Lucia Poláčková | consulting, strategy | medium | 14 |
| expert-5 | David Tóth | speaking, ai | low | 9 |

## 🔌 Integrations Ready

### Email
- Auto-confirmation emails
- Expert match notifications
- Auto-reply system
- Uses Nodemailer (configurable SMTP)

### Notion
- Export requests to CSV/JSON
- Export expert database
- Sync status monitoring
- Bi-directional sync ready

## 🎨 Customization

### Add New Categories
Edit `server/services/requestService.js` - `categorizeRequest()` method

### Adjust Prioritization
Edit `server/services/requestService.js` - `prioritizeRequest()` method

### Change Styling
Edit `client/src/App.css`

### Add More Experts
Edit `server/database.js` - `experts` array

## 🚨 Troubleshooting

**Port already in use:**
```bash
# Change port in server/index.js (line with PORT)
# Or kill process: npx kill-port 3001
```

**CORS errors:**
```bash
# Make sure backend is running on :3001
# Frontend proxy is set in vite.config.js
```

**Module not found:**
```bash
# Reinstall dependencies
rm -rf node_modules client/node_modules
npm install && cd client && npm install && cd ..
```

## 💡 Next Steps

- [ ] Add database persistence (PostgreSQL)
- [ ] User authentication
- [ ] Real Notion API integration
- [ ] WebSocket real-time notifications
- [ ] Advanced search/filtering
- [ ] Admin dashboard
- [ ] Leaderboards & gamification
- [ ] Mobile app

## 📝 Project Files

```
hackathon2026/
├── server/
│   ├── index.js              (Express server)
│   ├── database.js           (Demo data)
│   ├── services/
│   │   └── requestService.js (Business logic)
│   └── routes/
│       ├── requests.js       (REST API)
│       ├── matchmaking.js    (Expert matching)
│       ├── email.js          (Notifications)
│       └── notion.js         (Notion sync)
├── client/
│   ├── src/
│   │   ├── App.jsx           (Main component)
│   │   ├── App.css           (Styles)
│   │   ├── main.jsx          (Entry)
│   │   └── components/
│   │       ├── Dashboard.jsx
│   │       ├── RequestList.jsx
│   │       ├── Matchmaking.jsx
│   │       ├── NewRequestForm.jsx
│   │       └── ExpertProfiles.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── package.json
├── README.md                 (Full documentation)
├── QUICKSTART.md             (This file)
└── API_TESTING.md            (API docs)
```

## 🎉 You're Ready!

Open http://localhost:3000 and start exploring! 🚀

---

**Created for HalovaMake Hackathon 2026**
