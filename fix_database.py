#!/usr/bin/env python
import os
import sys

# Проверяем наличие переменной окружения DATABASE_URL
db_url = os.environ.get('DATABASE_URL', '')
print(f"DATABASE_URL: {'отсутствует' if not db_url else db_url}")

# Если URL отсутствует или имеет неправильный формат, устанавливаем SQLite
if not db_url or not (db_url.startswith('postgresql://') or db_url.startswith('postgres://')):
    print("Устанавливаем подключение к SQLite...")
    os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'
    print("✅ Установлено подключение к SQLite")
    sys.exit(0)

# Создаем файл с настройками для Django
with open('database_config.py', 'w') as f:
    f.write("""
# Автоматически созданный файл для настройки подключения к базе данных
import os
import dj_database_url

# Настройка базы данных
if 'DATABASE_URL' in os.environ:
    db_url = os.environ.get('DATABASE_URL')
    # Для отладки - выводим URL (скрываем пароль)
    if '@' in db_url:
        user_pass, rest = db_url.split('@', 1)
        if ':' in user_pass:
            user, _ = user_pass.split(':', 1)
            masked_url = f"{user}:******@{rest}"
            print(f"DATABASE_URL: {masked_url}")

    # Используем dj_database_url для настройки
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3',
            conn_max_age=600,
            ssl_require=False
        )
    }
else:
    # Если DATABASE_URL не задан, используем SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }
    print("Используется SQLite для базы данных")
""")

print("✅ Создан файл настроек базы данных")
