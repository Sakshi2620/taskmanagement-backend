# Task Management Backend (Django REST API)

Django REST API for a simple task management app.

## Features
- CRUD APIs for tasks
- Task fields: `title`, `description`, `status`, `created_at`
- CORS configured for local Vite dev and production frontend

## Requirements
- Python 3.12+

## Setup (local)
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

## API Endpoints
- List/Create: `GET/POST /api/tasks/`
- Retrieve/Update/Delete: `GET/PATCH/PUT/DELETE /api/tasks/<id>/`

Example:
- `http://127.0.0.1:8000/api/tasks/`

## Environment variables
Local defaults work, but for production set:
```env
DEBUG=False
SECRET_KEY=your-secret
ALLOWED_HOSTS=your-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.onrender.com
```

If using Render Postgres, also set:
```env
DATABASE_URL=postgres://...
```

## Deploy on Render (Web Service)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn backend.wsgi:application`
- After first deploy, run in Render Shell:
  - `python manage.py migrate`
