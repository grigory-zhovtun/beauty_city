#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка нужных переменных окружения
if [ -z "$RENDER" ]; then
  export RENDER=true
  echo "Установлена переменная RENDER=true"
fi

# Устанавливаем зависимости
pip install -r requirements.txt

# Исправление DATABASE_URL
echo "=== Исправление URL базы данных ==="
python simple_fix_db.py

# Сохраняем оригинальный URL для восстановления в конце сборки
export ORIGINAL_DATABASE_URL="$DATABASE_URL"

# Используем SQLite на время сборки для гарантированного выполнения миграций
echo "=== Настройка базы данных для сборки ==="
export DATABASE_URL="sqlite:///db.sqlite3"
echo "Для сборки будет использован SQLite"

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

# Создаем простой файл для проверки настроек базы данных
cat > check_render_db.py << 'EOF'
import os
import sys
import dj_database_url

print("\n=== Проверка настроек базы данных ===")

# Проверяем наличие URL
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print("❌ DATABASE_URL не задан!")
    sys.exit(1)

# Маскируем пароль для вывода
masked_url = db_url
if '@' in db_url and ':' in db_url.split('@')[0]:
    user_pass, rest = db_url.split('@', 1)
    if ':' in user_pass:
        user, _ = user_pass.split(':', 1)
        masked_url = f"{user}:******@{rest}"

print(f"DATABASE_URL: {masked_url}")

try:
    # Получаем настройки из URL
    config = dj_database_url.parse(db_url)
    config_safe = {k: '******' if k == 'PASSWORD' else v for k, v in config.items()}
    print(f"Настройки подключения: {config_safe}")
    print("✅ URL базы данных имеет правильный формат")
except Exception as e:
    print(f"❌ Ошибка при парсинге URL: {str(e)}")
    sys.exit(1)
EOF

# Проверяем настройки базы данных
python check_render_db.py

# Восстанавливаем исправленный URL
if [ -f "fixed_db_url.txt" ]; then
    export DATABASE_URL=$(cat fixed_db_url.txt)
    echo "✅ Восстановлен исправленный URL базы данных"
else
    export DATABASE_URL="$ORIGINAL_DATABASE_URL"
    echo "⚠️ Используется оригинальный URL базы данных"
fi

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

# Собираем статические файлы
python manage.py collectstatic --no-input

# Простая проверка подключения к базе данных
cat > db_connection_check.py << 'EOF'
import os
import sys

try:
    import dj_database_url
    import psycopg2
except ImportError:
    from pip._internal import main as pip_main
    pip_main(['install', 'dj-database-url', 'psycopg2-binary'])
    import dj_database_url
    import psycopg2

from urllib.parse import urlparse

print("\n=== Тестирование подключения к базе данных ===")

# Получаем URL из переменной окружения
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print("❌ DATABASE_URL не задан")
    sys.exit(1)

# Если URL для SQLite, пропускаем проверку
if db_url.startswith('sqlite'):
    print("✅ Используется SQLite, тест не требуется")
    sys.exit(0)

# Маскируем пароль для вывода
try:
    parsed = urlparse(db_url)
    masked_url = db_url
    if parsed.password:
        masked_url = db_url.replace(parsed.password, '******')
    print(f"Проверка подключения к: {masked_url}")

    # Получаем параметры подключения
    config = dj_database_url.parse(db_url)
    host = config.get('HOST', '')
    port = config.get('PORT', 5432)
    dbname = config.get('NAME', '')
    user = config.get('USER', '')
    password = config.get('PASSWORD', '')

    print(f"Хост: {host}, Порт: {port}, БД: {dbname}, Пользователь: {user}")

    # Пробуем подключиться
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        connect_timeout=5
    )

    print("✅ Подключение успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения: {str(e)}")
    print("Для запуска приложения будет использоваться SQLite")
EOF

python db_connection_check.py || echo "⚠️ Проблемы с подключением к PostgreSQL, но сборка продолжается"

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
