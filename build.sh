#!/usr/bin/env bash
# Render build script
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

cd src
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser from env vars (only if it doesn't already exist)
if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser --noinput 2>/dev/null || echo "Superuser already exists."
fi
