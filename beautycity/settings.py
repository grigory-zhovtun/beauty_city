import os
import dj_database_url
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
   ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

SECRET_KEY = os.getenv('SECRET_KEY', 'REPLACE_ME')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

MANAGER_PHONE = os.getenv('MANAGER_PHONE', '+7 (***) ***-**-**')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'salon',
    'rest_framework',
    'bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': dj_database_url.config(
           default='sqlite:///db.sqlite3',
           conn_max_age=600,
           ssl_require=False  # Отключаем требование SSL для локальной разработки
    )

}

# Настройка базы данных для Render
if 'RENDER' in os.environ:
    print("\n=== Настройка базы данных для Render ===")

    # Получаем текущий DATABASE_URL (если есть)
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url:
        # Для безопасности: выводим URL, но скрываем пароль
        parts = db_url.split('@')
        if len(parts) > 1:
            auth = parts[0].split(':', 1)
            if len(auth) > 1:
                masked_url = f"{auth[0]}:******@{parts[1]}"
                print(f"Оригинальный DATABASE_URL: {masked_url}")

    # Обновляем настройки базы данных
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=False
    )

    # Для отладки: вывод конфигурации
    config_copy = DATABASES['default'].copy()
    if 'PASSWORD' in config_copy:
        config_copy['PASSWORD'] = '******'  # Скрываем пароль
    print(f"Конфигурация базы данных: {config_copy}")

ROOT_URLCONF = 'beautycity.urls'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa: E501
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa: E501
    },
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Bot settings - moved to a separate module to avoid circular imports
# The bot will be initialized in the bot app's ready() method
