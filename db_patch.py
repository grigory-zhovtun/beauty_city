import os
import sys
import re

# Получаем URL базы данных
db_url = os.environ.get('DATABASE_URL', '')

if not db_url:
    print("Ошибка: DATABASE_URL не задан!")
    sys.exit(1)

# Извлекаем компоненты URL с помощью регулярного выражения
pattern = r'postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+)(?::([0-9]+))?/([^?]+)'
matches = re.match(pattern, db_url)

if not matches:
    print(f"Ошибка: Не удалось разобрать DATABASE_URL: {db_url}")
    sys.exit(1)

username, password, host, port, dbname = matches.groups()
port = port or '5432'  # Используем порт по умолчанию, если не указан

# Проверяем, нужно ли заменить хост
if 'dpg-' in host and '.render.com' not in host:
    # Используем localhost вместо проблемного хоста
    print(f"Заменяем хост {host} на localhost")
    host = 'localhost'

# Устанавливаем переменные для Django
new_db_url = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
os.environ['DATABASE_URL'] = new_db_url

print(f"Настроен новый URL базы данных: {new_db_url}")
