# API Status and Testing Notes

This document explains the current API situation so testing matches reality.

## Current active product path

The active product is the Django web app run with:

```bash
python manage.py runserver
```

Main usage currently goes through Django templates and views.

## DRF layer exists but is not currently routed

The codebase includes DRF components:

- `server/viewsets.py`
- `server/serializers.py`

These define viewsets for:

- categories
- experts
- requests
- expert matches

However, `server/urls.py` does not currently register these viewsets through a router (`DefaultRouter`/`SimpleRouter`) and does not expose `/api/...` endpoints for this layer.

## Legacy Node demo layer

The repository still contains a legacy Node/Express demo:

- `package.json`
- `server/index.js`
- `server/routes/`
- `server/services/`

Treat this as historical/demo code unless you explicitly decide to run and maintain it.

## How to test right now

### Option A: Test active web workflow (recommended)

1. Run Django server.
2. Log in via `accounts/login/`.
3. Submit a request via `submit/`.
4. Validate dashboard state updates.
5. Validate expert assignment and completion flow.

### Option B: Expose DRF router first, then test with curl

If you want REST endpoints, first wire `server/viewsets.py` into `server/urls.py`. After that, test endpoints such as:

- `/api/requests/`
- `/api/experts/`
- `/api/categories/`
- `/api/matches/`

## Recommended test checklist

### Web flow

- registration/login works
- request submission works
- dashboard updates
- super-admin assignment works
- requester completion confirmation works

### DRF flow (after routing)

- `GET /api/requests/`
- `GET /api/experts/`
- `GET /api/categories/`
- `GET /api/matches/`
- detail and action endpoints based on viewset wiring

## Bottom line

For immediate product validation, test the Django web flow.

For API testing, first enable DRF routing explicitly and then run endpoint tests.
