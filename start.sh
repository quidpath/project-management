#!/bin/bash
set -e

# Only load .env file if not in dev mode (docker-compose sets env vars directly)
if [ -f /app/.env ] && [ "$DJANGO_ENV" != "dev" ]; then
  export $(grep -v '^#' /app/.env | tr -d '\r' | xargs)
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser..."
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || echo "Superuser already exists"
else
  echo "Skipping superuser creation - environment variables not set"
fi

echo "Starting Daphne (ASGI)..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} projects_service.asgi:application
