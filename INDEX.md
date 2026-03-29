# Documentation Index

Use this index to quickly navigate project documentation and key code locations.

## Root documentation files

- `README.md`: product overview and architecture notes
- `QUICKSTART.md`: fastest startup path
- `SETUP.md`: complete setup and role behavior
- `API_TESTING.md`: current API reality and test options
- `INTERNAL_COORDINATION.md`: internal workflow and responsibilities

## Core code locations

### `server/models.py`

Main domain models:

- `Request`
- `Expert`
- `Category`
- `Skill`
- `Language`
- chat models
- `WorkerProfile`

### `server/views.py`

Main web workflow:

- landing pages
- authentication pages
- request submission
- role-based dashboards
- request detail and request chat
- worker management

### `server/forms.py`

Forms for:

- request submission and review
- registration and profile editing
- chat messages

### `server/templates/`

Main UI templates:

- `index.html`
- `about.html`
- `features.html`
- `how_it_works.html`
- `dashboard.html`
- `admin_dashboard.html`
- `request_detail.html`
- `request_chat.html`

### `server/tasks.py`

Matching and asynchronous-capable background logic.

### `server/chat_utils.py`

Chat helpers for read-state, mute, and channel behavior.

## Navigation by intent

### Update landing and informational copy

Edit templates in `server/templates/` and the associated context in `server/views.py`.

### Modify matching and assignment behavior

Check `server/views.py`, `server/tasks.py`, and `server/models.py`.

### Modify worker role scoping

Check `WorkerProfile` in `server/models.py` and worker-related views in `server/views.py`.

### Enable API routing

Compare `server/viewsets.py` with `server/urls.py` and add router wiring.
