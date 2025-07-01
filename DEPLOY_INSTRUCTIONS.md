# Инструкции по деплою на Render

## Настройка на Render

1. **Создайте два сервиса на Render:**
   - Web Service для Django приложения
   - Background Worker для Telegram бота

2. **Настройте переменные окружения:**
   ```
   DATABASE_URL=<ваша PostgreSQL база>
   SECRET_KEY=<секретный ключ Django>
   TELEGRAM_TOKEN=<токен вашего бота>
   ALLOWED_HOSTS=<ваш домен на Render>
   RENDER_EXTERNAL_HOSTNAME=<автоматически от Render>
   WEBHOOK_URL=https://<ваш-домен>.onrender.com (опционально для webhook)
   MANAGER_PHONE=<телефон менеджера>
   ```

3. **Для Web Service:**
   - Build Command: `./build.sh`
   - Start Command: `gunicorn beautycity.wsgi:application`

4. **Для Background Worker:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run_bot.py`

## Применение миграций

После деплоя зайдите в Shell на Render и выполните:

```bash
# Проверьте статус миграций
python manage.py showmigrations

# Примените миграцию для создания недостающих таблиц
python manage.py migrate salon 0002_create_missing_tables

# Проверьте, что таблицы созданы
python manage.py dbshell
\dt salon_*
\q
```

## Режимы работы бота

- **Polling mode** (по умолчанию): Бот сам забирает обновления
- **Webhook mode**: Установите переменную WEBHOOK_URL для активации

## Проверка работы

1. Откройте вашего бота в Telegram
2. Отправьте команду /start
3. Проверьте логи в Render Dashboard