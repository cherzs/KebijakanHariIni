# KawalKebijakan

Policy tracker Indonesia — membantu publik memahami kebijakan pemerintah dalam 30 detik.

## Quick Start

```bash
# Start infrastructure
docker compose up -d

# Backend
cd backend
pip install -r requirements.txt
python seed_db.py
uvicorn app.main:app --reload --port 8000

# Celery worker (separate terminal)
cd backend
celery -A app.tasks.celery_app worker --loglevel=info

# Frontend (separate terminal)
cd frontend
npm run dev
```

Admin: `admin@kawalkebijakan.id` / `admin123`

## Architecture

- **Frontend**: Next.js + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL 16
- **Queue**: Celery + Redis
- **AI**: OpenAI / DeepSeek / Groq (provider-agnostic)

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── core/            # Config, DB, security
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── tasks/            # Celery tasks
│   ├── scrapers/             # Web scrapers
│   └── seed_db.py
├── frontend/
│   └── src/
│       ├── app/              # Next.js pages
│       ├── components/       # React components
│       └── lib/              # API client, types
└── docker-compose.yml
```