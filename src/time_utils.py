from datetime import datetime, timedelta
import dateutil


def get_local_timezone():
    return dateutil.tz.tzlocal()


def get_threshold(time: datetime, interval: int):
    return time + timedelta(seconds=interval)


def get_delta_to_threshold(time: datetime, interval: int):
    now_with_tz = datetime.now(tz=get_local_timezone())
    delta = get_threshold(time, interval) - now_with_tz
    return delta


def get_delta_to_now(time: datetime):
    now_with_tz = datetime.now(tz=get_local_timezone())
    delta = now_with_tz - time
    return delta


def is_in_time_range(time: datetime, interval: int):
    if 0 <= get_delta_to_threshold(time, interval).total_seconds() <= interval:
        return True
    return False


def is_after_threshold(time: datetime, interval: int):
    delta = get_delta_to_now(time)
    if interval < delta.total_seconds():
        return True
    return False


def get_now_with_timezone():
    return datetime.now(tz=get_local_timezone())
