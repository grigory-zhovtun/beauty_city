#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Apply database migrations
# First, fake unapply the initial migration for salon to ensure all operations are re-run
python manage.py migrate salon 0001_initial --fake-initial --fake
# Then, apply all migrations
python manage.py migrate
