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
python manage.py createsuperuser --noinput || true

echo "Starting Daphne (ASGI)..."
exec daphne -b 0.0.0.0 -p 8007 projects_service.asgi:application
