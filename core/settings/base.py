import os
import sys
import datetime
from celery.schedules import crontab
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

TEST_RUNNING = 'test' in sys.argv

SECRET_KEY = 'django-insecure-0xc!6lko8cofh#=9i_3-aw^ed=&nts%pb4_0sl8f*v8$m&gly)'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django_celery_beat'
]

LOCAL_APPS = [
    "users",
    "utils",
    "activity_logger",
    "watchlist",
    "signalapp",
    "ui_app",
    "main",
    "exchange_app"
]

INSTALLED_APPS = INSTALLED_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_URL = '/static/'

MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'utils.drf.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.CustomTokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ]
}

CORS_ALLOW_CREDENTIALS = True

HTTP_ONLY_TOKEN_KEY = "token"

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_SERVER = f"redis://{REDIS_HOST}:{REDIS_PORT}"

CELERY_BROKER_URL = REDIS_SERVER
CELERY_RESULT_BACKEND = REDIS_SERVER
CELERY_BEAT_SCHEDULE = {
    'get-bitunix-symbols-task': {
        'task': 'exchange_app.tasks.get_bitunix_symbols_task',
        'schedule': crontab(hour=3, minute=35),
    },
    'get-bitunix-exchange-transactions-task': {
        'task': 'exchange_app.tasks.get_bitunix_exchange_transactions_task',
        'schedule': datetime.timedelta(seconds=45),
    },
    'check-engulfing-strategy-task': {
        'task': 'exchange_app.tasks.check_engulfing_strategy_task',
        'schedule': datetime.timedelta(seconds=30)
    }
}
