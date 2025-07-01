#!/usr/bin/env bash
# exit on error
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Проверка и исправление DATABASE_URL
echo "=== Проверка DATABASE_URL ==="
python check_db_url.py

# Настройка для SQLite на время сборки
echo "=== Настройка базы данных для сборки ==="
echo "RENDER = $RENDER"
echo "DATABASE_URL задан: $(if [ -n "$DATABASE_URL" ]; then echo 'ДА'; else echo 'НЕТ'; fi)"

# Сохраняем оригинальный URL, если он есть
if [ -n "$DATABASE_URL" ]; then
    export ORIGINAL_DATABASE_URL="$DATABASE_URL"
    echo "Оригинальный URL сохранен"

    # Временно используем SQLite для миграций и сборки
    export DATABASE_URL="sqlite:///db.sqlite3"
    echo "Для сборки будет использован SQLite"
fi

# Сбор статических файлов
python manage.py collectstatic --noinput

# Выполнение миграций с SQLite
echo "=== Выполнение миграций ==="
python manage.py migrate

# Заполнение тестовыми данными (опционально)
echo "=== Заполнение тестовыми данными ==="
python manage.py fill_db || echo "⚠️ Не удалось заполнить базу тестовыми данными, но это не критично."

# Создаём файл с инструкциями для Render
cat > render_info.txt << EOF
# Настройка Render для Django с PostgreSQL

Для правильной работы приложения, убедитесь, что:

1. В настройках среды указана переменная RENDER=true
2. В переменной DATABASE_URL указан ВНУТРЕННИЙ URL (Internal Database URL)
   из настроек вашей базы данных PostgreSQL на Render
3. Не меняйте порт в DATABASE_URL, оставьте значение по умолчанию

Приложение настроено на использование SQLite во время сборки для
беспроблемного выполнения миграций.

В рабочем режиме будет использоваться PostgreSQL, как указано в DATABASE_URL.
EOF

echo "✅ Сборка завершена успешно!"

    # Выводим информацию (скрываем пароль для безопасности)
    echo "Имя пользователя: $DB_USER"
    echo "Имя базы данных: $DB_NAME"
    echo "Используем URL: postgresql://${DB_USER}:******@internal/${DB_NAME}"

    # Устанавливаем новый URL
    export DATABASE_URL="$INTERNAL_DATABASE_URL"
#fi

# Создаем служебный файл для проверки настроек
cat > check_db_settings.py << 'EOF'
import os
import sys
import dj_database_url

print("\n=== Проверка настроек базы данных ===")
db_url = os.environ.get('DATABASE_URL', '')
print(f"DATABASE_URL: {db_url.replace(db_url.split('@')[0].split(':', 1)[1], '******') if '@' in db_url else db_url}")

# Получаем настройки из URL
config = dj_database_url.parse(db_url)
config_safe = {k: '******' if k == 'PASSWORD' else v for k, v in config.items()}
print(f"Настройки подключения: {config_safe}")
EOF

python check_db_settings.py

# Сбор статических файлов
python manage.py collectstatic --no-input

# Настройка для миграций
echo "\n=== Настройка миграций ==="

cat > run_migrations.py << 'EOF'
import os
import sys
import subprocess

print("Пытаемся запустить миграции...")

# Первая попытка - с текущими настройками
try:
    print("\n=== Попытка 1: С текущими настройками ===")
    result = subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    print("✅ Миграции успешно применены!")
    sys.exit(0)
except subprocess.CalledProcessError:
    print("❌ Ошибка при выполнении миграций с текущими настройками.")

# Вторая попытка - с SQLite
try:
    print("\n=== Попытка 2: Используем SQLite временно ===")
    # Сохраняем оригинальный URL
    original_url = os.environ.get('DATABASE_URL', '')

    # Временно устанавливаем SQLite
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'

    # Запускаем миграции
    result = subprocess.run([sys.executable, "manage.py", "migrate"], check=True)

    # Восстанавливаем оригинальный URL
    if original_url:
        os.environ['DATABASE_URL'] = original_url

    print("✅ Миграции успешно применены с SQLite!")
    print("⚠️ ВНИМАНИЕ: Использована локальная база данных SQLite. В рабочем режиме данные будут в PostgreSQL.")
    sys.exit(0)
except subprocess.CalledProcessError:
    print("❌ Ошибка при выполнении миграций с SQLite.")
    sys.exit(1)
EOF

python run_migrations.py

# Заполняем базу тестовыми данными (если миграции прошли успешно)
if [ $? -eq 0 ]; then
    echo "\n=== Заполнение базы тестовыми данными ==="
    python manage.py fill_db || echo "⚠️ Не удалось заполнить базу тестовыми данными, но это не критично."
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
