#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Вывод отладочной информации
echo "=== Проверка настроек базы данных ==="
echo "RENDER = $RENDER"
echo "DATABASE_URL задан: $(if [ -n "$DATABASE_URL" ]; then echo 'ДА'; else echo 'НЕТ'; fi)"

# Создаём дополнительные варианты URL для базы данных
if [[ -n "$DATABASE_URL" && "$DATABASE_URL" == *"@dpg-"* && "$DATABASE_URL" != *"render.com"* ]]; then
    # Извлекаем компоненты URL
    DB_CREDENTIALS=$(echo "$DATABASE_URL" | sed -E 's/(.*@).*$/\1/')
    DB_HOST=$(echo "$DATABASE_URL" | sed -E 's/.*@([^/]+)\/.*/\1/')
    DB_NAME=$(echo "$DATABASE_URL" | sed -E 's/.*\/(.*)$/\1/')

    # Создаём разные варианты URL для тестирования
    export PGHOST_EXTERNAL="${DB_HOST}.postgres.render.com"
    export PGHOST_INTERNAL="postgres"
    export PGHOST_INTERNAL2="postgres.internal"
    export PGHOST_SPECIFIC="dpg-${DB_HOST#dpg-}"

    echo "Оригинальный хост: $DB_HOST"
    echo "Имя базы данных: $DB_NAME"
    echo "Пробуем разные варианты хостов:"
    echo "1. ${PGHOST_EXTERNAL}"
    echo "2. ${PGHOST_INTERNAL}"
    echo "3. ${PGHOST_INTERNAL2}"
    echo "4. ${PGHOST_SPECIFIC}"

    # Установка переменных для тестирования
    export DATABASE_URL_EXTERNAL="${DB_CREDENTIALS}${PGHOST_EXTERNAL}/${DB_NAME}"
    export DATABASE_URL_INTERNAL="${DB_CREDENTIALS}${PGHOST_INTERNAL}/${DB_NAME}"
    export DATABASE_URL_INTERNAL2="${DB_CREDENTIALS}${PGHOST_INTERNAL2}/${DB_NAME}"
    export DATABASE_URL_SPECIFIC="${DB_CREDENTIALS}${PGHOST_SPECIFIC}/${DB_NAME}"

    # Используем внешний хост для начала
    export DATABASE_URL="$DATABASE_URL_EXTERNAL"
fi

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

# Проверка подключения к базе данных
cat > db_connection_test.py << 'EOF'
import os
import sys
import psycopg2
from urllib.parse import urlparse
import time

print("\n=== Тестирование подключения к базе данных ===")

# Проверяем оригинальный URL
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print("ОШИБКА: DATABASE_URL не задан!")
    sys.exit(1)

print(f"Тестирование URL: {db_url.replace(urlparse(db_url).password, '******')}")

# Проверяем основной URL
def test_connection(url, name):
    try:
        result = urlparse(url)
        dbname = result.path.lstrip('/')
        user = result.username
        password = result.password
        host = result.hostname
        port = result.port or 5432

        print(f"\nПытаемся подключиться к {name}: {host}:{port}/{dbname}")

        # Пробуем подключиться
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=10
        )

        print(f"✅ Подключение к {name} успешно!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ ОШИБКА при подключении к {name}: {str(e)}")
        return False

# Пробуем основной URL
if not test_connection(db_url, "основному URL"):
    # Проверяем альтернативные URL
    alternatives = [
        (os.environ.get('DATABASE_URL_EXTERNAL', ''), "внешнему хосту"),
        (os.environ.get('DATABASE_URL_INTERNAL', ''), "внутреннему хосту"),
        (os.environ.get('DATABASE_URL_INTERNAL2', ''), "внутреннему хосту 2"),
        (os.environ.get('DATABASE_URL_SPECIFIC', ''), "специфичному хосту"),
    ]

    for alt_url, name in alternatives:
        if alt_url and test_connection(alt_url, name):
            print(f"\n✅ Успешное подключение к {name}. Используем этот URL.")
            os.environ['DATABASE_URL'] = alt_url
            print(f"Установлен новый DATABASE_URL: {alt_url.replace(urlparse(alt_url).password, '******')}")
            break
EOF

python db_connection_test.py

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
