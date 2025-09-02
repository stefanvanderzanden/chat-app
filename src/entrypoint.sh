#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "🔧 Fixing permissions for static & media..."
chown -R app-user:app-user /home/app-user/app/staticfiles /home/app-user/app/media

echo "Starting server..."
exec uvicorn _project.asgi:application --host 0.0.0.0 --port 8000
