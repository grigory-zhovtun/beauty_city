#!/usr/bin/env python
import os
import sys
from urllib.parse import urlparse, urlunparse

def fix_database_url():
    # Получаем URL базы данных
    db_url = os.environ.get('DATABASE_URL', '')

    if not db_url:
        print("DATABASE_URL не задан, будет использован SQLite")
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
        return

    # Маскируем пароль для логов
    masked_url = db_url
    if '@' in db_url:
        parts = db_url.split('@')
        if len(parts) > 1 and ':' in parts[0]:
            credentials = parts[0].split(':', 1)
            if len(credentials) > 1:
                masked_url = f"{credentials[0]}:******@{parts[1]}"

    print(f"Проверка URL базы данных: {masked_url}")

    # Проверяем схему URL
    if db_url.startswith('://'):
        fixed_url = f"postgresql{db_url}"
        os.environ['DATABASE_URL'] = fixed_url
        print(f"Исправлен URL: схема добавлена")
        db_url = fixed_url

    try:
        # Парсим URL
        parsed = urlparse(db_url)
        scheme = parsed.scheme or 'postgresql'
        netloc = parsed.netloc
        path = parsed.path
        params = parsed.params
        query = parsed.query
        fragment = parsed.fragment

        # Если хост содержит dpg- (Render PostgreSQL)
        if 'dpg-' in netloc:
            # Извлекаем компоненты netloc (username:password@host:port)
            host_parts = netloc.split('@')

            if len(host_parts) > 1:
                auth = host_parts[0]
                host_port = host_parts[1].split(':')

                # Заменяем хост на localhost
                new_host = 'localhost'
                new_netloc = f"{auth}@{new_host}"

                # Если был указан порт, сохраняем его
                if len(host_port) > 1:
                    new_netloc = f"{new_netloc}:{host_port[1]}"

                # Собираем новый URL
                new_url_components = (scheme, new_netloc, path, params, query, fragment)
                new_url = urlunparse(new_url_components)

                os.environ['DATABASE_URL'] = new_url
                print("✅ URL базы данных изменен: хост заменен на localhost")
    except Exception as e:
        print(f"⚠️ Ошибка при обработке URL базы данных: {str(e)}")
        print("Будет использован оригинальный URL")

# Проверяем доступность хостов PostgreSQL
def check_pg_hosts():
    import socket

    hosts_to_check = ['db', 'database', 'postgres', 'postgres.internal', 'localhost']
    available_hosts = []
    port = 5432

    print("\nПроверка доступных хостов PostgreSQL...")

    for host in hosts_to_check:
        try:
            print(f"Проверка {host}:{port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)  # Таймаут 2 секунды
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                print(f"✅ Хост {host} доступен на порту {port}")
                available_hosts.append(host)
            else:
                print(f"❌ Ошибка подключения к {host}: {result}")
        except socket.gaierror:
            print(f"❌ Ошибка подключения к {host}: could not translate host name \"{host}\" to address: Name or service not known")
        except Exception as e:
            print(f"❌ Ошибка подключения к {host}: {str(e)}")

    if available_hosts:
        print(f"\n✅ Доступные хосты PostgreSQL: {', '.join(available_hosts)}")
        # Используем первый доступный хост
        return available_hosts[0]
    else:
        print("⚠️ Не удалось подключиться ни к одному хосту PostgreSQL")
        print("Переключение на SQLite...")
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
        return None

if __name__ == "__main__":
    # Исправляем URL базы данных
    fix_database_url()

    # Проверяем доступные хосты
    available_host = check_pg_hosts()

    # Если есть доступный хост, изменяем DATABASE_URL
    if available_host and available_host not in ['localhost', '127.0.0.1']:
        db_url = os.environ.get('DATABASE_URL', '')
        if db_url and '@' in db_url:
            try:
                parts = db_url.split('@')
                auth = parts[0]
                rest = parts[1].split('/', 1)

                # Замена хоста на доступный
                if len(rest) > 1:
                    new_url = f"{auth}@{available_host}/{rest[1]}"
                else:
                    new_url = f"{auth}@{available_host}"

                os.environ['DATABASE_URL'] = new_url
                print(f"DATABASE_URL обновлен с использованием доступного хоста: {available_host}")
            except Exception as e:
                print(f"Ошибка при обновлении URL: {str(e)}")
