from django.apps import AppConfig


class ActivityLoggerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activity_logger'

    def ready(self) -> None:
        from activity_logger import signals, handlers