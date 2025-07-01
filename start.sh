#!/usr/bin/env bash
# Скрипт запуска Django на Render
set -o errexit

# Убедимся, что RENDER установлен
if [ -z "$RENDER" ]; then
  export RENDER=true
fi

# Исправляем DATABASE_URL если нужно
python simple_fix_db.py

# Применяем миграции к рабочей базе данных
echo "=== Применение миграций ==="
python manage.py migrate || echo "⚠️ Ошибка при выполнении миграций, но продолжаем запуск"

# Выводим информацию о запуске
echo "=== Запуск приложения ==="
echo "RENDER = $RENDER"

# Безопасный вывод DATABASE_URL (скрываем пароль)
if [ -n "$DATABASE_URL" ]; then
  MASKED_URL=$(echo "$DATABASE_URL" | sed -E 's/(\/\/[^:]+:)[^@]+(@)/\1******\2/')
  echo "DATABASE_URL: $MASKED_URL"
else
  echo "DATABASE_URL не задан, будет использоваться SQLite"
fi

# Запуск Django
if [ -n "$PORT" ]; then
    # Запуск через gunicorn, если установлен порт
    echo "Запуск через gunicorn на порту $PORT"
    gunicorn beautycity.wsgi:application --bind 0.0.0.0:$PORT
else
    # Запуск через стандартный сервер Django
    echo "Запуск через Django dev server на порту 8000"
    python manage.py runserver 0.0.0.0:8000
fi
