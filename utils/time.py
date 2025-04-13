import datetime, logging
from django.utils.timesince import timesince


logger = logging.getLogger(__name__)


def custom_timesince(d: datetime.date) -> str:
    since = timesince(d)
    try:
        since = since.split(',')[0]
        digit = int(since.split()[0])
        if digit < 1:
            return 'Just now'
    except Exception as e:
        logger.error(e, exc_info=1)
        pass
    return f'{since} ago'