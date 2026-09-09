#!/bin/sh
set -u

echo "[start.sh] booting - PORT=${PORT:-unset} DATABASE_URL set=$([ -n "${DATABASE_URL:-}" ] && echo yes || echo no) SUPABASE_URL set=$([ -n "${SUPABASE_URL:-}" ] && echo yes || echo no) CORS_ORIGINS raw=${CORS_ORIGINS:-<empty>}"

cd /app/backend

export CORS_ORIGINS="$(python -c 'import json, os; raw = os.getenv("CORS_ORIGINS", "").strip();
try:
    parsed = json.loads(raw) if raw else []
except json.JSONDecodeError:
    parsed = [item.strip().strip("\\\"") for item in raw.split(",") if item.strip()]
if isinstance(parsed, str):
    parsed = [parsed]
print(json.dumps(parsed))')"
echo "[start.sh] normalized CORS_ORIGINS=$CORS_ORIGINS"

python -c 'import json, os; print("window.__ROOTED_CONFIG__ = " + json.dumps({"supabaseUrl": os.getenv("SUPABASE_URL", ""), "supabaseAnonKey": os.getenv("SUPABASE_ANON_KEY", "")}) + ";")' > /usr/share/nginx/html/config.js
echo "[start.sh] wrote /usr/share/nginx/html/config.js"

envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/conf.d/default.conf
echo "[start.sh] rendered nginx config for PORT=${PORT:-8080}"

# Migrations are logged loudly but are NOT allowed to take the whole
# container down - if they fail, the app still starts so the failure is
# visible through the browser/network tab and Railway's health check still
# passes, instead of a silent "Application failed to respond" 502 with zero
# diagnostic information.
if alembic upgrade head; then
    echo "[start.sh] alembic upgrade head: OK"
else
    echo "[start.sh] *** alembic upgrade head FAILED (exit $?) - starting anyway so logs/errors are reachable. Check DATABASE_URL. ***" >&2
fi

uvicorn app.main:app --host 127.0.0.1 --port 8000 &
backend_pid=$!
echo "[start.sh] uvicorn started, pid=$backend_pid"

cleanup() {
    kill "$backend_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "[start.sh] starting nginx on port ${PORT:-8080}"
nginx -g 'daemon off;'
