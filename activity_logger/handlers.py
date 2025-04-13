from django.dispatch import receiver
from channels.db import database_sync_to_async
from .signals import action, action_bulk
from .models import Log, LogDetail
from .utils import get_target, get_details


@database_sync_to_async
@receiver(action)
def action_handler(**kwargs):
    kwargs.pop('signal')
    kwargs.pop('sender')
    kwargs = get_target(**kwargs)
    details, kwargs = get_details(**kwargs)
    log = Log.objects.create(**kwargs)
    if details:
        details = [LogDetail(log=log, **detail) for detail in details]
        LogDetail.objects.bulk_create(details, batch_size=1000)


@database_sync_to_async
@receiver(action_bulk)
def action_bulk_handler(**kwargs):
    kwargs.pop('signal')
    kwargs.pop('sender')
    logs = kwargs.get('logs')
    logs_for_create = []
    log_details_for_create = []
    for log in logs:
        log = get_target(**log)
        details, log = get_details(**log)
        log = Log(**log)
        logs_for_create.append(log)
        if details:
            details = [LogDetail(log=log, **detail) for detail in details]
            log_details_for_create += details
    logs = Log.objects.bulk_create(
        logs_for_create, 
        batch_size=1000
    )
    if log_details_for_create:
        LogDetail.objects.bulk_create(log_details_for_create, batch_size=1000)