#!/usr/bin/env bash
# Скрипт для настройки и проверки подключения к базе данных
set -o errexit

echo "=== Настройка подключения к базе данных ==="

# Проверка DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
  echo "❌ Переменная DATABASE_URL не задана"
  echo "Будет использоваться SQLite"
  export DATABASE_URL="sqlite:///db.sqlite3"
else
  # Проверка формата URL
  if [[ ! "$DATABASE_URL" =~ ^postgresql://.*$ && ! "$DATABASE_URL" =~ ^postgres://.*$ ]]; then
    echo "❌ DATABASE_URL имеет неверный формат: $DATABASE_URL"
    echo "URL должен начинаться с postgresql:// или postgres://"

    # Пытаемся исправить URL
    if [[ "$DATABASE_URL" == *"postgres"* && "$DATABASE_URL" == *"@"* ]]; then
      if [[ "$DATABASE_URL" == "://"* ]]; then
        NEW_URL="postgresql${DATABASE_URL}"
      elif [[ ! "$DATABASE_URL" == *"://"* ]]; then
        NEW_URL="postgresql://${DATABASE_URL}"
      else
        NEW_URL="postgresql://${DATABASE_URL#*://}"
      fi
      echo "✅ Исправлен URL: $NEW_URL"
      export DATABASE_URL="$NEW_URL"
    else
      echo "⚠️ Не удалось исправить URL, будет использоваться SQLite"
      export DATABASE_URL="sqlite:///db.sqlite3"
    fi
  else
    echo "✅ DATABASE_URL имеет правильный формат"
  fi

  # Маскировка пароля для вывода
  MASKED_URL=$(echo "$DATABASE_URL" | sed -E 's/(\/\/[^:]+:)[^@]+(@)/\1******\2/')
  echo "Используется URL: $MASKED_URL"
fi

# Создаем тестовый скрипт для проверки подключения
cat > test_connection.py << 'EOF'
import os
import sys
import time

try:
    import dj_database_url
    from urllib.parse import urlparse
    import psycopg2
except ImportError:
    print("Установка необходимых пакетов...")
    from pip._internal import main as pip_main
    pip_main(['install', 'dj-database-url', 'psycopg2-binary'])
    import dj_database_url
    from urllib.parse import urlparse
    import psycopg2

db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print("❌ DATABASE_URL не задан")
    sys.exit(1)

if db_url.startswith('sqlite'):
    print("✅ Используется SQLite, проверка не требуется")
    sys.exit(0)

# Маскируем пароль для вывода
try:
    parsed = urlparse(db_url)
    masked_url = db_url
    if parsed.password:
        masked_url = db_url.replace(parsed.password, '******')
    print(f"Проверка подключения к: {masked_url}")

    # Получаем параметры подключения
    db_config = dj_database_url.parse(db_url)
    host = db_config.get('HOST')
    port = db_config.get('PORT', 5432)
    dbname = db_config.get('NAME')
    user = db_config.get('USER')
    password = db_config.get('PASSWORD')

    print(f"Хост: {host}, Порт: {port}, БД: {dbname}, Пользователь: {user}")

    # Пробуем подключиться
    start = time.time()
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
        connect_timeout=10
    )

    # Проверяем версию
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    conn.close()

    elapsed = time.time() - start
    print(f"✅ Подключение успешно! ({elapsed:.2f} сек)")
    print(f"PostgreSQL версия: {version}")
except Exception as e:
    print(f"❌ Ошибка подключения: {str(e)}")

    # Пробуем альтернативные хосты
    print("\nПроверка альтернативных хостов:")
    alternative_hosts = ['postgres.internal', 'postgres', 'localhost', '127.0.0.1']

    success = False
    for alt_host in alternative_hosts:
        if alt_host == host:
            continue

        print(f"\nПроверка хоста: {alt_host}")
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=alt_host,
                port=port,
                connect_timeout=5
            )
            print(f"✅ Подключение к {alt_host} успешно!")
            print(f"Рекомендация: Используйте хост {alt_host} в DATABASE_URL")

            # Создаем новый URL с рабочим хостом
            parsed = urlparse(db_url)
            scheme = parsed.scheme
            netloc = f"{user}:{password}@{alt_host}:{port}"
            path = f"/{dbname}"
            fixed_url = f"{scheme}://{netloc}{path}"

            # Сохраняем рабочий URL в файл
            with open('working_db_url.txt', 'w') as f:
                f.write(fixed_url)

            print(f"Рабочий URL сохранен в файл working_db_url.txt")

            conn.close()
            success = True
            break
        except Exception as e:
            print(f"❌ Ошибка при подключении к {alt_host}: {str(e)}")

    if not success:
        print("\n❌ Не удалось подключиться ни к одному хосту")
        print("Рекомендация: Проверьте настройки базы данных и сетевое подключение")
        sys.exit(1)
EOF

echo "\n=== Проверка подключения к базе данных ==="
python test_connection.py

# Проверяем, был ли найден рабочий URL
if [ -f "working_db_url.txt" ]; then
  echo "\n=== Обновление DATABASE_URL ==="
  WORKING_URL=$(cat working_db_url.txt)
  # Маскируем пароль для вывода
  MASKED_URL=$(echo "$WORKING_URL" | sed -E 's/(\/\/[^:]+:)[^@]+(@)/\1******\2/')
  echo "Найден рабочий URL: $MASKED_URL"
  export DATABASE_URL="$WORKING_URL"
  echo "✅ DATABASE_URL обновлен"
  rm working_db_url.txt
fi

echo "\n=== Настройка базы данных завершена ==="
