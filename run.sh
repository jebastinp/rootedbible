#!/usr/bin/env bash
# =====================================================================
# Rooted - one-click local start (Mac/Linux)
#
# Usage:  ./run.sh
#
# What it does:
#   1. Creates backend/.env and frontend/.env from .env.example if missing
#   2. Creates a Python venv + installs backend deps (only if not already done)
#   3. Installs frontend deps (only if not already done)
#   4. Starts the FastAPI backend (port 8001) and Vite frontend (port 5173)
#   5. Ctrl+C stops both
#
# First-time setup you still must do yourself before this works fully:
#   - Create a Supabase project and run database/schema.sql in its SQL editor
#   - Put your Supabase connection string into backend/.env (DATABASE_URL)
# Until you do that, the backend will start but API calls that hit the
# database will fail - that's expected on a totally fresh checkout.
# =====================================================================
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "🌱 Rooted — starting up..."
echo ""

# ---------------------------------------------------------------
# Backend
# ---------------------------------------------------------------
cd "$BACKEND_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  Created backend/.env from .env.example."
  echo "   Edit backend/.env and set DATABASE_URL to your Supabase connection string,"
  echo "   then re-run ./run.sh."
  echo ""
fi

if [ ! -d venv ]; then
  echo "📦 Creating Python virtual environment (first run only)..."
  python3 -m venv venv
fi

# shellcheck source=/dev/null
source venv/bin/activate

echo "📦 Checking backend dependencies..."
pip install -q -r requirements.txt

echo "🚀 Starting backend on http://localhost:8001 ..."
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

deactivate

# ---------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------
cd "$FRONTEND_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
fi

if [ ! -d node_modules ]; then
  echo "📦 Installing frontend dependencies (first run only, this can take a minute)..."
  npm install
fi

echo "🚀 Starting frontend on http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "──────────────────────────────────────────────"
echo "🌱  Rooted is running:"
echo "    App:      http://localhost:5173"
echo "    API docs: http://localhost:8001/api/docs"
echo ""
echo "    First login (seeded super admin): ADMIN001"
echo "──────────────────────────────────────────────"
echo ""
echo "Press Ctrl+C to stop both servers."

cleanup() {
  echo ""
  echo "🛑 Stopping Rooted..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

wait
