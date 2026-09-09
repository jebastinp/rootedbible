#!/bin/sh
set -eu

cd /app/backend
envsubst '${PORT}' < /app/nginx.conf.template > /etc/nginx/conf.d/default.conf
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
backend_pid=$!

cleanup() {
    kill "$backend_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

nginx -g 'daemon off;'