#!/usr/bin/env python
import os
import sys

# Проверяем DATABASE_URL
db_url = os.environ.get('DATABASE_URL', '')
print(f"Текущий DATABASE_URL: {'[не задан]' if not db_url else db_url}")

# Проверяем формат URL
if not db_url:
    print("ОШИБКА: DATABASE_URL не задан!")
    # Устанавливаем SQLite по умолчанию
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    print("Установлен DATABASE_URL для SQLite: sqlite:///db.sqlite3")
    sys.exit(0)

# Проверяем схему URL
if '://' not in db_url or db_url.startswith('://'):
    print(f"ОШИБКА: Неверный формат URL: {db_url}")
    # Проверяем, есть ли в URL строка postgres или postgresql
    if 'postgres' in db_url:
        # Пытаемся исправить URL
        if not db_url.startswith('postgresql://'):
            fixed_url = f"postgresql://{db_url.lstrip('://')}" if '://' in db_url else f"postgresql://{db_url}"
            os.environ['DATABASE_URL'] = fixed_url
            print(f"Исправлен URL: {fixed_url}")
    else:
        # Устанавливаем SQLite по умолчанию
        os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
        print("Установлен DATABASE_URL для SQLite: sqlite:///db.sqlite3")
    sys.exit(0)

print("✅ DATABASE_URL имеет корректный формат")
