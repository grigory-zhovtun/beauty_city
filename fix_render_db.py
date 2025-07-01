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
#!/usr/bin/env python
"""
Скрипт для исправления URL базы данных на Render
Добавьте его в директорию проекта и вызовите перед запуском бота
"""
import os
import sys
from urllib.parse import urlparse, urlunparse

# Получаем URL базы данных из переменной окружения
db_url = os.environ.get('DATABASE_URL', '')

if not db_url:
    print("⚠️ DATABASE_URL не задан")
    sys.exit(0)

# Безопасный вывод URL (скрываем пароль)
masked_url = db_url
try:
    parsed = urlparse(db_url)
    if parsed.password:
        user_pass = f"{parsed.username}:******"
        netloc = parsed.netloc.replace(f"{parsed.username}:{parsed.password}", user_pass)
        masked_url = urlunparse((parsed.scheme, netloc, parsed.path, 
                               parsed.params, parsed.query, parsed.fragment))
except Exception:
    pass

print(f"Исходный DATABASE_URL: {masked_url}")

try:
    # Парсим URL для получения компонентов
    parsed_url = urlparse(db_url)

    # Проверяем хост
    hostname = parsed_url.hostname

    if hostname and 'dpg-' in hostname:
        print(f"Найден проблемный хост: {hostname}")

        # Создаем новые компоненты URL с исправленным хостом
        new_netloc = parsed_url.netloc.replace(hostname, 'postgres.internal')

        # Собираем новый URL
        new_url_components = (
            parsed_url.scheme,
            new_netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        )
        new_url = urlunparse(new_url_components)

        # Устанавливаем новый URL в переменную окружения
        os.environ['DATABASE_URL'] = new_url

        # Безопасный вывод нового URL (скрываем пароль)
        masked_new_url = new_url
        try:
            new_parsed = urlparse(new_url)
            if new_parsed.password:
                user_pass = f"{new_parsed.username}:******"
                netloc = new_parsed.netloc.replace(f"{new_parsed.username}:{new_parsed.password}", user_pass)
                masked_new_url = urlunparse((new_parsed.scheme, netloc, new_parsed.path, 
                                          new_parsed.params, new_parsed.query, new_parsed.fragment))
        except Exception:
            pass

        print(f"✅ URL базы данных исправлен: {masked_new_url}")
    else:
        print("✅ URL базы данных не требует исправлений")

except Exception as e:
    print(f"❌ Ошибка при обработке URL базы данных: {str(e)}")
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
