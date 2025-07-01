# Подробная инструкция по деплою BeautyCity на Render

## Предварительные требования

1. Аккаунт на [Render.com](https://render.com)
2. Аккаунт на GitHub с вашим репозиторием проекта
3. Telegram Bot Token от [@BotFather](https://t.me/botfather)

## Шаг 1: Подготовка кода к деплою

### 1.1 Проверьте наличие всех необходимых файлов:
- ✅ `requirements.txt` - зависимости проекта
- ✅ `build.sh` - скрипт сборки
- ✅ `Procfile` - конфигурация процессов
- ✅ `run_bot.py` - запуск бота
- ✅ `runtime.txt` (опционально) - версия Python

### 1.2 Создайте файл runtime.txt (если его нет):
```
python-3.11.0
```

### 1.3 Убедитесь, что build.sh исполняемый:
```bash
chmod +x build.sh
```

### 1.4 Закоммитьте все изменения:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Шаг 2: Создание базы данных PostgreSQL на Render

1. Войдите в [Render Dashboard](https://dashboard.render.com)
2. Нажмите **New +** → **PostgreSQL**
3. Заполните форму:
   - **Name**: `beautycity-db`
   - **Database**: оставьте пустым (создастся автоматически)
   - **User**: оставьте пустым (создастся автоматически)
   - **Region**: выберите ближайший к вам регион
   - **PostgreSQL Version**: 15
   - **Datadog API Key**: оставьте пустым
4. Выберите план:
   - Для тестирования: **Free** ($0/month)
   - Для продакшена: **Starter** ($7/month)
5. Нажмите **Create Database**
6. Дождитесь создания БД (5-10 минут)
7. Скопируйте **Internal Database URL** из вкладки Info

## Шаг 3: Создание Web Service для Django

1. В Render Dashboard нажмите **New +** → **Web Service**
2. Выберите **Build and deploy from a Git repository**
3. Подключите ваш GitHub аккаунт и выберите репозиторий
4. Заполните настройки:

### Basic Settings:
- **Name**: `beautycity-web`
- **Region**: тот же, что и у БД
- **Branch**: `main` (или ваша основная ветка)
- **Root Directory**: оставьте пустым
- **Runtime**: `Python 3`

### Build & Deploy:
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn beautycity.wsgi:application`

### Instance Type:
- Для тестирования: **Free** ($0/month)
- Для продакшена: **Starter** ($7/month)

### Environment Variables:
Нажмите **Add Environment Variable** и добавьте:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Internal Database URL из шага 2 |
| `SECRET_KEY` | Сгенерируйте безопасный ключ |
| `TELEGRAM_TOKEN` | Токен вашего бота от BotFather |
| `ALLOWED_HOSTS` | `.onrender.com,localhost` |
| `PYTHON_VERSION` | `3.11.0` |
| `MANAGER_PHONE` | Телефон менеджера |

### Генерация SECRET_KEY:
```python
# Выполните в Python консоли:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

5. Нажмите **Create Web Service**
6. Дождитесь первого деплоя (10-15 минут)

## Шаг 4: Создание Background Worker для бота

1. В Render Dashboard нажмите **New +** → **Background Worker**
2. Выберите тот же репозиторий
3. Заполните настройки:

### Basic Settings:
- **Name**: `beautycity-bot`
- **Region**: тот же, что и у БД
- **Branch**: `main`
- **Root Directory**: оставьте пустым
- **Runtime**: `Python 3`

### Build & Deploy:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run_bot.py`

### Instance Type:
- **Starter** ($7/month) - рекомендуется для стабильной работы

### Environment Variables:
Скопируйте все переменные из Web Service:
- `DATABASE_URL`
- `SECRET_KEY`
- `TELEGRAM_TOKEN`
- `PYTHON_VERSION`
- `DJANGO_SETTINGS_MODULE` = `beautycity.settings`

4. Нажмите **Create Background Worker**

## Шаг 5: Применение миграций

1. Дождитесь успешного деплоя Web Service
2. В Render Dashboard откройте ваш Web Service
3. Перейдите во вкладку **Shell**
4. Выполните команды:

```bash
# Проверка подключения к БД
python manage.py dbshell
\l
\q

# Проверка статуса миграций
python manage.py showmigrations

# Применение всех миграций
python manage.py migrate

# Применение миграции для недостающих таблиц
python manage.py migrate salon 0002_create_missing_tables

# Создание суперпользователя (опционально)
python manage.py createsuperuser
```

## Шаг 6: Настройка Webhook (опционально)

Для улучшения производительности можно настроить webhook:

1. В Environment Variables добавьте:
   - `WEBHOOK_URL` = `https://beautycity-web.onrender.com`
   
2. В `beautycity/urls.py` убедитесь, что есть путь:
```python
path('webhook/', webhook_view, name='webhook'),
```

## Шаг 7: Проверка работы

### 7.1 Проверка Django:
1. Откройте `https://beautycity-web.onrender.com/admin/`
2. Войдите с учетными данными суперпользователя
3. Проверьте доступность админ-панели

### 7.2 Проверка бота:
1. Откройте вашего бота в Telegram
2. Отправьте команду `/start`
3. Проверьте, что бот отвечает

### 7.3 Мониторинг логов:
- Web Service: вкладка **Logs** в Render Dashboard
- Bot Worker: вкладка **Logs** в Render Dashboard

## Шаг 8: Настройка домена (опционально)

1. Во вкладке **Settings** вашего Web Service
2. В секции **Custom Domain** добавьте ваш домен
3. Настройте DNS записи согласно инструкции Render
4. Обновите `ALLOWED_HOSTS` в Environment Variables

## Troubleshooting

### Ошибка "relation salon_admin does not exist"
```bash
# В Shell выполните:
python manage.py migrate salon 0002_create_missing_tables --fake-initial
```

### Бот не отвечает
1. Проверьте логи Background Worker
2. Убедитесь, что `TELEGRAM_TOKEN` правильный
3. Проверьте, что все переменные окружения установлены

### Ошибки импорта модулей
```bash
# В Shell выполните:
pip list  # проверьте установленные пакеты
python -c "import django; print(django.__version__)"
```

### База данных недоступна
1. Проверьте статус PostgreSQL в Render Dashboard
2. Убедитесь, что `DATABASE_URL` правильный
3. Проверьте, что все сервисы в одном регионе

## Полезные команды для Shell

```bash
# Очистка миграций (осторожно!)
python manage.py migrate salon zero
python manage.py migrate salon

# Проверка подключения к БД
python manage.py dbshell -c "SELECT version();"

# Сброс кеша
python manage.py clear_cache

# Проверка настроек
python manage.py diffsettings

# Список всех URL
python manage.py show_urls
```

## Мониторинг и обслуживание

1. **Автоматические деплои**: Render автоматически деплоит при push в GitHub
2. **Метрики**: доступны во вкладке Metrics каждого сервиса
3. **Алерты**: настройте уведомления в Settings → Notifications
4. **Бэкапы БД**: для платных планов доступны автоматические бэкапы

## Стоимость

### Минимальный набор для продакшена:
- PostgreSQL Starter: $7/month
- Web Service Starter: $7/month  
- Background Worker Starter: $7/month
- **Итого**: $21/month

### Для тестирования:
- PostgreSQL Free: $0/month (ограничения: 90 дней жизни)
- Web Service Free: $0/month (ограничения: 750 часов/месяц)
- Background Worker Starter: $7/month (нет бесплатного плана)
- **Итого**: $7/month

## Контакты поддержки

- Render Support: https://render.com/support
- Документация: https://render.com/docs
- Статус сервисов: https://status.render.com/

---

После успешного деплоя ваш бот BeautyCity будет доступен 24/7!