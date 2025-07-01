#!/usr/bin/env python
import os
import sys
from urllib.parse import urlparse, urlunparse

# Получаем текущий URL
db_url = os.environ.get('DATABASE_URL', '')
print(f"Оригинальный DATABASE_URL: {db_url}")

# Проверяем наличие URL
if not db_url:
    print("❌ DATABASE_URL не задан!")
    sys.exit(1)

# Если URL начинается с '://'
if db_url.startswith('://'):
    # Добавляем postgresql в начало
    db_url = f"postgresql{db_url}"
    print(f"Исправлен URL: {db_url}")
    os.environ['DATABASE_URL'] = db_url

# Проверяем схему URL
if not (db_url.startswith('postgresql://') or db_url.startswith('postgres://')):
    print(f"❌ Некорректная схема URL: {db_url}")

    # Пытаемся исправить - добавляем схему postgresql://
    if '@' in db_url and ':' in db_url.split('@')[0]:
        db_url = f"postgresql://{db_url}"
        print(f"Исправлен URL: {db_url}")
        os.environ['DATABASE_URL'] = db_url
    else:
        print("❌ Невозможно исправить URL автоматически")
        sys.exit(1)

# Преобразуем URL для Render
try:
    parsed = urlparse(db_url)
    scheme = parsed.scheme if parsed.scheme else 'postgresql'
    netloc = parsed.netloc
    path = parsed.path

    # Извлекаем компоненты netloc
    if '@' in netloc:
        userpass, hostport = netloc.split('@', 1)

        # Если хост содержит dpg- (Render external URL)
        if 'dpg-' in hostport and not '.render.com' in hostport:
            print(f"Внешний хост Render обнаружен: {hostport}")
            hostport = 'postgres.internal:5432'
            print(f"Заменен на внутренний хост: {hostport}")

        netloc = f"{userpass}@{hostport}"

    # Собираем URL обратно
    fixed_url = urlunparse((scheme, netloc, path, '', '', ''))

    print(f"Итоговый URL: {fixed_url}")
    os.environ['DATABASE_URL'] = fixed_url

    # Сохраняем URL в файл для использования в build.sh
    with open('fixed_db_url.txt', 'w') as f:
        f.write(fixed_url)
    print("✅ URL сохранен в файл fixed_db_url.txt")

    print("✅ DATABASE_URL успешно исправлен!")
except Exception as e:
    print(f"❌ Ошибка при обработке URL: {str(e)}")
    sys.exit(1)
