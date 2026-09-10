FROM node:20-alpine AS frontend-build
WORKDIR /frontend

ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app/backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx gettext-base gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
# Content-licensing registry (app/content/licensing.py resolves this at
# /app/licensing/translations.json) - just the reviewed-and-hashed registry,
# never the underlying evidence documents or Bible source XML, both of
# which stay out of the image/repo entirely.
COPY licensing/translations.json /app/licensing/translations.json
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html
COPY nginx.conf.template /app/nginx.conf.template
COPY start.sh /app/start.sh

EXPOSE 8080
CMD ["sh", "/app/start.sh"]