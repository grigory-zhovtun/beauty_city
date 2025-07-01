#!/usr/bin/env python
import os
import sys
import time
from urllib.parse import urlparse

try:
    import dj_database_url
    import psycopg2
except ImportError:
    print("Устанавливаем необходимые пакеты...")
    from pip._internal import main as pip_main
    pip_main(['install', 'dj-database-url', 'psycopg2-binary'])
    import dj_database_url
    import psycopg2

print("\n=== Тестирование подключения к базе данных ===")

# Получаем URL базы данных
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print("ОШИБКА: DATABASE_URL не задан!")
    sys.exit(1)

# Безопасный вывод URL (скрываем пароль)
masked_url = db_url
try:
    parsed = urlparse(db_url)
    if parsed.password:
        masked_url = db_url.replace(parsed.password, '******')
except Exception:
    pass

print(f"Тестирование URL: {masked_url}")

# Проверяем схему URL
if not db_url.startswith('postgresql://') and not db_url.startswith('postgres://'):
    print(f"ОШИБКА: URL должен начинаться с postgresql:// или postgres://")
    sys.exit(1)

# Парсим URL для получения компонентов
try:
    db_config = dj_database_url.parse(db_url)
    print(f"Хост: {db_config.get('HOST')}")
    print(f"Порт: {db_config.get('PORT', '5432')}")
    print(f"База данных: {db_config.get('NAME')}")
    print(f"Пользователь: {db_config.get('USER')}")

    # Проверяем подключение
    print("\nПроверка подключения...")

    # Пробуем подключиться с таймаутом
    start_time = time.time()
    max_attempts = 3
    attempt = 1

    while attempt <= max_attempts:
        try:
            print(f"Попытка {attempt}/{max_attempts}...")
            conn = psycopg2.connect(
                dbname=db_config.get('NAME'),
                user=db_config.get('USER'),
                password=db_config.get('PASSWORD'),
                host=db_config.get('HOST'),
                port=db_config.get('PORT', '5432'),
                connect_timeout=10
            )
            print("✅ Подключение успешно!")

            # Дополнительная проверка - пытаемся выполнить запрос
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"PostgreSQL версия: {version}")

            cursor.close()
            conn.close()
            break
        except Exception as e:
            print(f"Ошибка подключения: {str(e)}")
            if attempt < max_attempts:
                wait_time = 2 * attempt  # Увеличиваем время ожидания с каждой попыткой
                print(f"Ждем {wait_time} секунд перед следующей попыткой...")
                time.sleep(wait_time)
            attempt += 1

    elapsed = time.time() - start_time
    if attempt > max_attempts:
        print(f"\n❌ Не удалось подключиться к базе данных после {max_attempts} попыток ({elapsed:.2f} сек)")

        # Предлагаем альтернативные хосты для тестирования
        alt_hosts = ['postgres', 'localhost', '127.0.0.1', 'db', 'postgresql']
        print("\nПробуем альтернативные хосты:")

        for alt_host in alt_hosts:
            if alt_host == db_config.get('HOST'):
                continue  # Пропускаем текущий хост

            print(f"\nТестирование хоста: {alt_host}")
            try:
                conn = psycopg2.connect(
                    dbname=db_config.get('NAME'),
                    user=db_config.get('USER'),
                    password=db_config.get('PASSWORD'),
                    host=alt_host,
                    port=db_config.get('PORT', '5432'),
                    connect_timeout=5
                )
                print(f"✅ Подключение к {alt_host} успешно!")
                print(f"Рекомендация: Используйте хост {alt_host} вместо {db_config.get('HOST')}")
                conn.close()
                break
            except Exception as e:
                print(f"Ошибка при подключении к {alt_host}: {str(e)}")

        sys.exit(1)
    else:
        print(f"\n✅ Тест подключения пройден за {elapsed:.2f} сек")

except Exception as e:
    print(f"\n❌ Ошибка при тестировании базы данных: {str(e)}")
    sys.exit(1)
