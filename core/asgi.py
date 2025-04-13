import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 
    f'core.settings.{os.environ.get("ENV", "dev")}'
)

application = get_asgi_application()
