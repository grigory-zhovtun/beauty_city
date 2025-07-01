#!/bin/bash
# Скрипт для запуска бота с исправлением URL базы данных

echo "===== Запуск бота с исправлением подключения к базе данных ====="

# Проверяем наличие DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
  echo "⚠️ Переменная DATABASE_URL не задана!"
  echo "Будет использована SQLite"
  export DATABASE_URL="sqlite:///db.sqlite3"
fi

# Исправляем URL базы данных, если он содержит dpg-
if [[ "$DATABASE_URL" == *"@dpg-"* ]]; then
  echo "Обнаружен проблемный URL базы данных: $DATABASE_URL"

  # Извлекаем префикс и суффикс
  PREFIX=$(echo $DATABASE_URL | cut -d'@' -f1)
  SUFFIX=$(echo $DATABASE_URL | cut -d'@' -f2 | cut -d'/' -f2-)

  # Создаем новый URL с localhost
  NEW_URL="${PREFIX}@localhost/${SUFFIX}"

  echo "✅ URL базы данных исправлен: $NEW_URL"
  export DATABASE_URL="$NEW_URL"
fi

# Проверяем подключение к базе данных
echo "Проверка подключения к базе данных..."
python test_db_connection.py

# Если проверка не прошла, используем SQLite
if [ $? -ne 0 ]; then
  echo "⚠️ Проблемы с подключением к PostgreSQL!"
  echo "Переключение на SQLite..."
  export DATABASE_URL="sqlite:///db.sqlite3"
fi

# Запускаем бота
echo "Запуск бота..."
python run_bot.py
