# 🚀 Quick Start - Index Website

Get the website running in 2 minutes!

## Step 1: Ensure Server is Running

```bash
python manage.py runserver
```

## Step 2: Visit the Website

Open your browser and go to:

```
http://localhost:8000/
```

## Available Pages

| Page                | URL              | Description                          |
| ------------------- | ---------------- | ------------------------------------ |
| **🏠 Home**         | `/`              | Landing page with stats and features |
| **📋 Features**     | `/features/`     | All features explained               |
| **📖 How It Works** | `/how-it-works/` | 6-step process                       |
| **ℹ️ About**        | `/about/`        | Project information                  |
| **📚 API Docs**     | `/api-docs/`     | REST API documentation               |
| **📝 Submit**       | `/submit/`       | Public request form                  |
| **👤 Admin**        | `/admin/`        | Django admin (login required)        |
| **📊 Dashboard**    | `/dashboard/`    | Admin dashboard (login required)     |

## Navigation

- **Top Navbar:** Links to all pages, action buttons
- **Home Page:** Quick overview of everything
- **Footer:** Links to key resources
- **Call-to-action:** Submit request buttons throughout

## What You Can Do

### Public Users (No Login)

- View home page
- Read about features
- Understand the process
- Read API docs
- Submit a request

### Admin Users (Login Required)

- View admin dashboard
- Review requests
- Assign experts
- Track statistics
- Manage system

## Key Features of the Website

✅ **Professional Design** - Modern purple gradient theme
✅ **Fully Responsive** - Works on mobile, tablet, desktop
✅ **Live Statistics** - Shows real data from database
✅ **Multiple Pages** - 6 comprehensive pages
✅ **API Docs** - Complete REST API documentation
✅ **Navigation** - Easy to browse all features
✅ **Responsive Grid** - Beautiful layouts
✅ **Inline CSS** - No external dependencies

## Files Created

```
server/templates/
├── base.html           (700 lines - Main template)
├── index.html          (180 lines - Home page)
├── about.html          (140 lines - About page)
├── features.html       (220 lines - Features)
├── how_it_works.html   (250 lines - Process)
└── api_docs.html       (290 lines - API docs)
```

## Updated Files

- `server/views.py` - Added 5 new view functions
- `server/urls.py` - Added 14 new URL routes
- `INDEX_WEBSITE.md` - Complete documentation

## Customization

### Change Colors

Edit color variables in `base.html`:

```css
--primary: #667eea; /* Main color */
--secondary: #764ba2; /* Secondary color */
```

### Change Text

Edit templates directly to change content

### Add New Pages

1. Create new view in `server/views.py`
2. Create new template in `server/templates/`
3. Add URL in `server/urls.py`
4. Add link in navbar (`base.html`)

## Troubleshooting

**Website not loading?**

- Ensure `python manage.py runserver` is running
- Check URL is `http://localhost:8000/`
- Clear browser cache (Ctrl+F5)

**Templates not found?**

- Ensure `TEMPLATES` is configured in `settings.py`
- Check templates folder exists: `server/templates/`
- Verify INSTALLED_APPS includes 'server'

**Styling is broken?**

- CSS is inline in `base.html`
- No external CSS files needed
- All styling in `<style>` tag

## Production Deployment

When deployed:

1. Set `DEBUG = False` in settings
2. Collect static files: `python manage.py collectstatic`
3. Use production web server (Gunicorn, uWSGI)
4. Setup database (PostgreSQL)
5. Configure email backend
6. Setup HTTPS/SSL

Site will work exactly the same way!

---

**Everything is ready to go!** 🎉

Visit http://localhost:8000/ and explore the website.
