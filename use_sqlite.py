#!/usr/bin/env python
"""
Скрипт для переключения на SQLite в случае проблем с PostgreSQL
"""
import os
import sys

print("Переключение на SQLite...")

# Сохраняем текущий URL для возможности восстановления
current_url = os.environ.get('DATABASE_URL', '')
if current_url:
    try:
        with open('original_db_url.txt', 'w') as f:
            f.write(current_url)
        print("Оригинальный URL сохранен в original_db_url.txt")
    except Exception as e:
        print(f"Ошибка при сохранении URL: {str(e)}")

# Устанавливаем SQLite
os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
print("✅ База данных переключена на SQLite")
print("ВНИМАНИЕ: Данные в SQLite не будут синхронизированы с PostgreSQL")
