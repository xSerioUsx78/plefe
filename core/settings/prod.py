from .base import *


HOME = str(Path.home())

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = int(os.environ.get("DEBUG", default="0")) == 1

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', default="127.0.0.1"),
        'PORT': int(os.environ.get('POSTGRES_PORT=5432', default=5432))
    }
}

MEDIA_ROOT = "/app/media"

STATIC_URL = '/static/'
STATIC_ROOT = "/app/staticfiles"

# CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS').split(',')

USE_LOGGING = int(os.environ.get('USE_LOGGING', default=0)) == 1

if USE_LOGGING:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} - {asctime} - {module} - {process} - {thread} - {message}',
                'style': '{'
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            'file_main': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'/app/main.log',
                'maxBytes': 1024*1024*20,  # 20 MB
                'backupCount': 5,
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['console', 'file_main'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
