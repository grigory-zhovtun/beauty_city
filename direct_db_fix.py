#!/usr/bin/env python
"""
Прямое исправление URL базы данных для Render
"""
import os
import sys
import psycopg2
import time

print("===== Прямое исправление подключения к базе данных =====")

# Получаем текущий URL
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print("⚠️ DATABASE_URL не задан! Будет использован SQLite.")
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    sys.exit(0)

# Маскируем пароль для вывода
masked_url = db_url
if '@' in db_url:
    prefix, rest = db_url.split('@', 1)
    if ':' in prefix:
        user, _ = prefix.split(':', 1)
        masked_url = f"{user}:******@{rest}"

print(f"Текущий URL: {masked_url}")

# Список возможных хостов для проверки
possible_hosts = ['localhost', '127.0.0.1', 'postgres', 'db', 'database']

# Извлекаем компоненты URL
if '@' in db_url:
    try:
        # Разбиваем URL на части
        prefix, rest = db_url.split('@', 1)

        # Извлекаем хост и порт
        if '/' in rest:
            host_port, path = rest.split('/', 1)
        else:
            host_port, path = rest, ''

        # Извлекаем хост и порт
        if ':' in host_port:
            host, port = host_port.split(':', 1)
        else:
            host, port = host_port, '5432'

        # Извлекаем учетные данные
        if ':' in prefix:
            user, password = prefix.split(':', 1)
        else:
            user, password = prefix, ''

        # Проверяем текущий хост
        print(f"Текущий хост: {host}, порт: {port}, база: {path}")

        # Пробуем подключиться с текущими настройками
        try:
            print(f"Проверка подключения к {host}:{port}/{path}...")
            conn = psycopg2.connect(
                dbname=path,
                user=user,
                password=password,
                host=host,
                port=port,
                connect_timeout=3
            )
            print(f"✅ Подключение к {host} успешно!")
            conn.close()
            sys.exit(0)  # Успешное подключение, выходим
        except Exception as e:
            print(f"❌ Ошибка подключения: {str(e)}")

        # Если не удалось подключиться, пробуем другие хосты
        print("Проверка альтернативных хостов...")
        for test_host in possible_hosts:
            if test_host == host:
                continue  # Пропускаем текущий хост

            try:
                print(f"Проверка {test_host}:{port}...")
                conn = psycopg2.connect(
                    dbname=path,
                    user=user,
                    password=password,
                    host=test_host,
                    port=port,
                    connect_timeout=3
                )
                print(f"✅ Подключение к {test_host} успешно!")

                # Обновляем URL базы данных
                new_url = f"{prefix}@{test_host}:{port}/{path}"
                os.environ['DATABASE_URL'] = new_url
                print(f"✅ URL базы данных обновлен: {user}:******@{test_host}:{port}/{path}")

                conn.close()
                sys.exit(0)  # Успешное подключение, выходим
            except Exception as e:
                print(f"❌ Ошибка подключения к {test_host}: {str(e)}")

        # Если все попытки не удались, используем SQLite
        print("⚠️ Не удалось подключиться ни к одному хосту PostgreSQL")
        print("Переключение на SQLite...")
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'

    except Exception as e:
        print(f"❌ Ошибка при обработке URL: {str(e)}")
        print("Переключение на SQLite...")
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
else:
    print(f"URL не содержит @: {db_url}")
    print("Переключение на SQLite...")
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
