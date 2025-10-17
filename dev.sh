#!/bin/sh

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django development server..."
exec gunicorn --bind 0.0.0.0:8000 --workers=3 --threads=4 --timeout=120 core.wsgi:application
