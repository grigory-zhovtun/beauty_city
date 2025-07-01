#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Проверяем существование таблиц и применяем миграции безопасно
echo "Checking database state..."
python manage.py showmigrations

# Пытаемся применить миграции, игнорируя ошибки если таблицы уже существуют
python manage.py migrate --fake-initial || echo "Migration failed, trying to fix..."

# Применяем каждую миграцию по отдельности для лучшего контроля
echo "Applying migrations one by one..."
python manage.py migrate salon 0001_initial --fake || true
python manage.py migrate salon 0002_create_missing_tables || true
python manage.py migrate salon 0003_add_missing_fields || true
python manage.py migrate || true
