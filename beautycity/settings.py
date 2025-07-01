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

# Настройка базы данных
# Проверяем наличие файла с настройками базы данных
try:
    from database_config import DATABASES
    print("Настройки базы данных загружены из database_config.py")
except ImportError:
    # Если файл не найден, используем стандартные настройки
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

    # Настройка базы данных из переменной окружения DATABASE_URL
    if 'DATABASE_URL' in os.environ:
        db_url = os.environ.get('DATABASE_URL')
        try:
            # Безопасное отображение URL (скрываем пароль)
            masked_url = db_url
            if '@' in db_url:
                parts = db_url.split('@')
                if len(parts) > 1 and ':' in parts[0]:
                    credentials = parts[0].split(':', 1)
                    if len(credentials) > 1:
                        masked_url = f"{credentials[0]}:******@{parts[1]}"
            print(f"Используется DATABASE_URL: {masked_url}")

            # Применяем настройки из DATABASE_URL
            db_config = dj_database_url.config(
                default='sqlite:///db.sqlite3',
                conn_max_age=600,
                ssl_require=False
            )
            DATABASES['default'] = db_config
            print(f"База данных настроена: {DATABASES['default'].get('ENGINE')}")
        except Exception as e:
            print(f"Ошибка при настройке базы данных: {str(e)}")
            print("Используется SQLite по умолчанию")

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
