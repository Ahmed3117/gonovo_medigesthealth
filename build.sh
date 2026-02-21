#!/usr/bin/env bash
# Render build script
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

cd src
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_data

# Create superuser from env vars (only if it doesn't already exist)
if [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    DJANGO_SUPERUSER_FIRST_NAME="${DJANGO_SUPERUSER_FIRST_NAME:-Admin}"
    DJANGO_SUPERUSER_LAST_NAME="${DJANGO_SUPERUSER_LAST_NAME:-User}"
    export DJANGO_SUPERUSER_FIRST_NAME DJANGO_SUPERUSER_LAST_NAME
    python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" --first_name "$DJANGO_SUPERUSER_FIRST_NAME" --last_name "$DJANGO_SUPERUSER_LAST_NAME" 2>/dev/null || echo "Superuser already exists."
fi
