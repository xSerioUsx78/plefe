from .base import *

SECRET_KEY = 'django-insecure-0xc!6lko8cofh#=9i_3-aw^ed=&nts%pb4_0sl8f*v8$m&gly)'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'plefe_base',
        'USER': 'plefe_user',
        'PASSWORD': 'plefe',
        'HOST': '127.0.0.1',
        "PORT": 5432
    }
}

if TEST_RUNNING:
    DATABASES['default']['NAME'] = 'plefe_test'
    DATABASES['default']['USER'] = 'plefe_user_test'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
