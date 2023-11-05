#!/bin/sh
set -e

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Start Gunicorn
gunicorn FARMS.wsgi:application --bind 0.0.0.0:80
