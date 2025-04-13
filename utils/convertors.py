import datetime
import zoneinfo
import calendar
from django.utils import timezone


def datetime_to_unix(obj: datetime.datetime) -> int:
    return int(calendar.timegm(obj.timetuple()))


def unix_to_datetime(time: int | float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(time, tz=timezone.utc)


def to_timezone(
    value: datetime.datetime,
    tz: str = timezone.get_default_timezone_name()
) -> datetime.datetime:
    return value.replace(
        tzinfo=zoneinfo.ZoneInfo("UTC")
    ).astimezone(zoneinfo.ZoneInfo(tz))
