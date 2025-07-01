#!/usr/bin/env bash
# Скрипт запуска Django на Render
set -o errexit

# Проверка переменных окружения
echo "=== Проверка настроек базы данных ==="
echo "RENDER = $RENDER"
echo "DATABASE_URL задан: $(if [ -n "$DATABASE_URL" ]; then echo 'ДА'; else echo 'НЕТ'; fi)"

# Выводим информацию о настройках БД
echo "=== Запуск приложения ==="

# Запуск Django
if [ -n "$PORT" ]; then
    # Запуск через gunicorn, если установлен порт
    gunicorn beautycity.wsgi:application --bind 0.0.0.0:$PORT
else
    # Запуск через стандартный сервер Django
    python manage.py runserver 0.0.0.0:8000
fi
