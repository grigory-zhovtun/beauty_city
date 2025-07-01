#!/usr/bin/env python
"""
Простой скрипт для исправления URL базы данных на Render
"""
import os
import sys

# Получаем URL базы данных из переменной окружения
db_url = os.environ.get('DATABASE_URL', '')

if not db_url:
    print("⚠️ DATABASE_URL не задан")
    sys.exit(0)

# Безопасный вывод URL (скрываем пароль)
masked_url = db_url
if '@' in db_url:
    try:
        prefix, rest = db_url.split('@', 1)
        if ':' in prefix:
            user, password = prefix.split(':', 1)
            masked_url = f"{user}:******@{rest}"
    except Exception:
        pass

print(f"Исходный DATABASE_URL: {masked_url}")

# Проверяем наличие dpg- в URL
if 'dpg-' in db_url:
    # Заменяем хост на localhost
    try:
        prefix, rest = db_url.split('@', 1)
        host_port, path = rest.split('/', 1) if '/' in rest else (rest, '')

        # Заменяем хост на localhost
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            new_host_port = f"localhost:{port}"
        else:
            new_host_port = "localhost:5432"

        # Собираем новый URL
        if path:
            new_url = f"{prefix}@{new_host_port}/{path}"
        else:
            new_url = f"{prefix}@{new_host_port}"

        os.environ['DATABASE_URL'] = new_url

        # Маскируем пароль для вывода
        masked_new_url = new_url
        if ':' in prefix:
            user, password = prefix.split(':', 1)
            masked_new_url = f"{user}:******@{new_host_port}/{path if path else ''}"

        print(f"✅ URL базы данных исправлен: {masked_new_url}")
    except Exception as e:
        print(f"❌ Ошибка при исправлении URL: {str(e)}")
else:
    print("✅ URL базы данных не требует исправлений")
