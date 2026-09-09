#!/bin/sh
set -eu

cd /app/backend
export CORS_ORIGINS="$(python -c 'import json, os; raw = os.getenv("CORS_ORIGINS", "").strip();
try:
    parsed = json.loads(raw) if raw else []
except json.JSONDecodeError:
    parsed = [item.strip().strip("\\\"") for item in raw.split(",") if item.strip()]
if isinstance(parsed, str):
    parsed = [parsed]
print(json.dumps(parsed))')"
python -c 'import json, os; print("window.__ROOTED_CONFIG__ = " + json.dumps({"supabaseUrl": os.getenv("SUPABASE_URL", ""), "supabaseAnonKey": os.getenv("SUPABASE_ANON_KEY", "")}) + ";")' > /usr/share/nginx/html/config.js
envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/conf.d/default.conf
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
backend_pid=$!

cleanup() {
    kill "$backend_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

nginx -g 'daemon off;'