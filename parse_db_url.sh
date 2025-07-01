#!/usr/bin/env bash
# Скрипт для обработки URL базы данных

# Проверяем, есть ли DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL не задан"
    exit 1
fi

# Выводим исходный URL (скрывая пароль)
masked_url=$(echo "$DATABASE_URL" | sed -E 's/(\/\/[^:]+:)[^@]+(@)/\1******\2/')
echo "Исходный URL: $masked_url"

# Проверяем, что это PostgreSQL URL
if [[ "$DATABASE_URL" != postgresql* ]]; then
    echo "❌ DATABASE_URL должен начинаться с postgresql://"
    exit 1
fi

# Извлекаем компоненты URL
DB_USER=$(echo "$DATABASE_URL" | sed -E 's/postgresql:\/\/([^:]+):.*/\1/')
DB_PASSWORD=$(echo "$DATABASE_URL" | sed -E 's/postgresql:\/\/[^:]+:([^@]+)@.*/\1/')
DB_HOST=$(echo "$DATABASE_URL" | sed -E 's/postgresql:\/\/[^:]+:[^@]+@([^:/]+).*/\1/')
DB_PORT=$(echo "$DATABASE_URL" | sed -E 's/.*@[^:]+:([0-9]+)\/.*/\1/;t;s/.*@[^:]+\/.*/5432/')
DB_NAME=$(echo "$DATABASE_URL" | sed -E 's/.*\/([^?]+)(\?.*)?$/\1/')

# Выводим компоненты
echo "Компоненты URL:"
echo "- Пользователь: $DB_USER"
echo "- Хост: $DB_HOST"
echo "- Порт: $DB_PORT"
echo "- База данных: $DB_NAME"

# Проверяем хост и заменяем, если нужно
if [[ "$DB_HOST" == dpg-* && "$DB_HOST" != *render.com ]]; then
    echo "⚠️ Проблемный хост: $DB_HOST"
    echo "✅ Заменяем на 'postgres.internal'"
    DB_HOST="postgres.internal"

    # Создаем новый URL
    NEW_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    echo "Новый URL: $(echo "$NEW_URL" | sed -E 's/(\/\/[^:]+:)[^@]+(@)/\1******\2/')"
    export DATABASE_URL="$NEW_URL"
fi

echo "✓ Обработка URL завершена"
