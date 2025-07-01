#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Вывод отладочной информации
echo "Проверка переменных окружения:"
echo "RENDER = $RENDER"
echo "DATABASE_URL задан: $(if [ -n "$DATABASE_URL" ]; then echo 'ДА'; else echo 'НЕТ'; fi)"
echo "Первые 10 символов DATABASE_URL: ${DATABASE_URL:0:10}..."

python manage.py collectstatic --no-input

# Apply database migrations
# First, fake unapply the initial migration for salon to ensure all operations are re-run
#python manage.py migrate salon 0001_initial --fake-initial --fake

# Явно устанавливаем переменную RENDER, если она еще не установлена
if [ -z "$RENDER" ]; then
  export RENDER=true
  echo "Установлена переменная RENDER=true"
fi

# Проверяем наличие DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
  echo "ОШИБКА: Переменная DATABASE_URL не установлена!"
  exit 1
fi

# Then, apply all migrations
python manage.py migrate
