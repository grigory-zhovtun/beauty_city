import os
import sys
import re
from urllib.parse import urlparse, urlunparse

# Получаем URL базы данных
db_url = os.environ.get('DATABASE_URL', '')

if not db_url:
    print("Ошибка: DATABASE_URL не задан!")
    # Устанавливаем SQLite по умолчанию
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    print("Установлен DATABASE_URL для SQLite: sqlite:///db.sqlite3")
    sys.exit(0)

# Проверяем формат URL
if not db_url.startswith('postgresql://') and not db_url.startswith('postgres://'):
    print(f"Предупреждение: DATABASE_URL имеет неверный формат: {db_url}")
    # Пробуем исправить URL
    if 'postgres' in db_url and '@' in db_url:
        # Пытаемся добавить схему
        if '://' not in db_url:
            db_url = f"postgresql://{db_url}"
            print(f"Исправлен URL: {db_url}")
    else:
        # Не можем исправить, используем SQLite
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
        print("Установлен DATABASE_URL для SQLite: sqlite:///db.sqlite3")
        sys.exit(0)

try:
    # Используем urlparse для более надежного парсинга
    parsed_url = urlparse(db_url)
    scheme = parsed_url.scheme
    username = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port or 5432
    path = parsed_url.path.lstrip('/')

    # Маскированный URL для вывода (скрываем пароль)
    masked_url = db_url
    if password:
        masked_url = db_url.replace(password, '******')
    print(f"Анализ URL: {masked_url}")
    print(f"Схема: {scheme}, Хост: {host}, Порт: {port}, База: {path}")

    # Проверяем и исправляем хост
    if host in ['internal', 'postgres.internal']:
        # Хост уже правильный для Render
        print(f"Хост {host} подходит для Render")
    elif host and ('dpg-' in host or host == 'localhost'):
        # Используем postgres.internal для Render
        print(f"Заменяем хост {host} на postgres.internal")
        host = 'postgres.internal'

    # Собираем новый URL
    new_scheme = 'postgresql'
    netloc = f"{username}:{password}@{host}" if username and password else host
    if port != 5432:
        netloc = f"{netloc}:{port}"

    new_url_tuple = (new_scheme, netloc, f"/{path}", '', '', '')
    new_db_url = urlunparse(new_url_tuple)

    # Устанавливаем новый URL
    os.environ['DATABASE_URL'] = new_db_url
    print(f"Настроен новый URL базы данных: {new_db_url.replace(password, '******') if password else new_db_url}")

except Exception as e:
    print(f"Ошибка при обработке URL: {str(e)}")
    # В случае ошибки используем SQLite
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    print("Установлен DATABASE_URL для SQLite из-за ошибки: sqlite:///db.sqlite3")
