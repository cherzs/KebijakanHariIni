#!/bin/bash
set -e

echo "=== KawalKebijakan Dev Setup ==="

echo "[1/4] Starting infrastructure..."
docker compose up -d
echo "Waiting for PostgreSQL..."
sleep 3

echo "[2/4] Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo "[3/4] Running migrations & seed..."
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine); print('Tables created')"
python seed_db.py

echo "[4/4] Installing frontend dependencies..."
cd ../frontend
npm install

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To start the backend:"
echo "  cd backend && uvicorn app.main:app --reload --port 8000"
echo ""
echo "To start the Celery worker:"
echo "  cd backend && celery -A app.tasks.celery_app worker --loglevel=info"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Admin credentials: admin@kawalkebijakan.id / admin123"