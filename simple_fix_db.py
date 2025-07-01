#!/usr/bin/env python
import os

# Получаем текущий DATABASE_URL
db_url = os.environ.get('DATABASE_URL', '')
print(f"Исходный DATABASE_URL: {db_url}")

# Если URL начинается с '://'
if db_url.startswith('://'):
    # Исправляем - добавляем postgresql
    fixed_url = f"postgresql{db_url}"
    os.environ['DATABASE_URL'] = fixed_url
    print(f"Исправленный DATABASE_URL: {fixed_url}")
    print("✅ URL успешно исправлен")
else:
    print("URL имеет корректный формат или отсутствует")
