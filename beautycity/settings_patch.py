import os
import sys
import dj_database_url
from urllib.parse import urlparse

# Определяем текущую директорию
settings_dir = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(settings_dir, 'settings.py')

# Проверяем, что файл настроек существует
if not os.path.exists(settings_path):
    print(f"ОШИБКА: Файл settings.py не найден по пути {settings_path}")
    sys.exit(1)

# Читаем оригинальный файл настроек
with open(settings_path, 'r') as f:
    settings_content = f.read()

# Проверяем, что переменные окружения для Render установлены
render_env = 'RENDER' in os.environ
database_url = os.environ.get('DATABASE_URL', '')

if render_env and database_url:
    # Обработка URL базы данных
    try:
        parsed_url = urlparse(database_url)
        hostname = parsed_url.hostname

        if hostname and 'dpg-' in hostname and '.render.com' not in hostname:
            # Создаем новый URL с хостом postgres
            username = parsed_url.username
            password = parsed_url.password
            port = parsed_url.port or 5432
            path = parsed_url.path.lstrip('/')

            # Используем новый хост для Render
            new_host = 'postgres'

            new_url = f"postgresql://{username}:{password}@{new_host}:{port}/{path}"
            os.environ['DATABASE_URL'] = new_url
            print(f"URL базы данных изменен на: postgresql://{username}:******@{new_host}:{port}/{path}")
    except Exception as e:
        print(f"ОШИБКА при обработке URL базы данных: {str(e)}")

# Проверяем, есть ли уже код для Render в settings.py
render_code_exists = 'RENDER' in settings_content and 'DATABASE_URL' in settings_content

# Если кода для Render нет, добавляем его
if not render_code_exists:
    # Находим секцию с базой данных
    database_section = "DATABASES = {"

    if database_section in settings_content:
        # Добавляем код настройки для Render
        render_config = """
# Настройка для Render
if 'RENDER' in os.environ:
    # Настройка базы данных для Render
    DATABASES['default'] = dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=False
    )
        """

        # Вставляем конфигурацию после секции DATABASES
        position = settings_content.find(database_section)
        if position != -1:
            # Находим конец блока DATABASES
            end_pos = settings_content.find("}", position)
            if end_pos != -1:
                end_pos = settings_content.find("}", end_pos + 1) + 1

                new_settings = settings_content[:end_pos] + render_config + settings_content[end_pos:]

                # Записываем обновленные настройки
                with open(settings_path, 'w') as f:
                    f.write(new_settings)
                print(f"Файл настроек {settings_path} успешно обновлен для Render.")
            else:
                print("ОШИБКА: Не удалось найти конец блока DATABASES")
        else:
            print("ОШИБКА: Не удалось найти секцию DATABASES в файле настроек")
    else:
        print("ОШИБКА: Секция DATABASES не найдена в файле настроек")
else:
    print("Файл настроек уже содержит конфигурацию для Render.")
