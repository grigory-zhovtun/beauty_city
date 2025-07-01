#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Вывод отладочной информации
echo "=== Проверка настроек базы данных ==="
echo "RENDER = $RENDER"
echo "DATABASE_URL задан: $(if [ -n "$DATABASE_URL" ]; then echo 'ДА'; else echo 'НЕТ'; fi)"

# Проверяем наличие EXTERNAL_URL в переменных окружения
if [ -n "$EXTERNAL_DATABASE_URL" ]; then
  echo "Используем EXTERNAL_DATABASE_URL для подключения к базе данных"
  export DATABASE_URL="$EXTERNAL_DATABASE_URL"
fi

# Вывод URL базы данных (скрывая пароль)
DISPLAY_URL=$(echo "$DATABASE_URL" | sed -r 's/([^:]+):([^@]+)@/\1:******@/')
echo "URL базы данных: $DISPLAY_URL"

# Добавим отладочный скрипт для проверки условий в settings.py
cat > debug_db.py << 'EOF'
import os
import dj_database_url

print("\n=== Отладка настроек базы данных ===")
print(f"RENDER в окружении: {'RENDER' in os.environ}")
print(f"DATABASE_URL в окружении: {'DATABASE_URL' in os.environ}")

if 'DATABASE_URL' in os.environ:
    db_url = os.environ.get('DATABASE_URL')
    print(f"URL базы данных: {db_url}")

    if 'dpg-' in db_url and '.render.com' not in db_url:
        print("Требуется замена хоста на localhost")
        db_parts = db_url.split('@')
        if len(db_parts) > 1:
            credentials = db_parts[0]
            host_and_path = db_parts[1].split('/')
            if len(host_and_path) > 1:
                db_path = '/'.join(host_and_path[1:])
                new_db_url = f"{credentials}@localhost/{db_path}"
                print(f"Новый URL: {new_db_url}")
    else:
        print("Замена хоста не требуется")

    # Проверяем парсинг dj_database_url
    db_config = dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600, ssl_require=False)
    print(f"Конфигурация БД: {db_config}")
    print(f"Хост в конфигурации: {db_config.get('HOST')}")
EOF

python debug_db.py

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

# Запускаем скрипт для исправления настроек базы данных
python db_patch.py

# Затем выполняем миграции с правильными настройками
DATABASE_URL_ORIGINAL="$DATABASE_URL"
export DATABASE_URL="$(python -c 'import os; print(os.environ.get("DATABASE_URL", "").replace("@dpg-", "@localhost/") if "@dpg-" in os.environ.get("DATABASE_URL", "") else os.environ.get("DATABASE_URL", ""))')"
echo "Измененный DATABASE_URL для миграций: $DATABASE_URL"

# Затем выполняем миграции
python manage.py migrate

# Восстанавливаем оригинальный URL
export DATABASE_URL="$DATABASE_URL_ORIGINAL"
