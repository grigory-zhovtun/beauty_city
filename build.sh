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

# Если миграция не удалась, помечаем первую миграцию как выполненную
if [ $? -ne 0 ]; then
    echo "Marking initial migration as applied..."
    python manage.py migrate salon 0001_initial --fake
    python manage.py migrate
fi
