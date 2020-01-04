from datetime import datetime, timedelta
import dateutil
import constants


def get_local_timezone():
    return dateutil.tz.tzlocal()


def is_in_time_range(time: datetime):
    threshold = time + timedelta(seconds=constants.POLLING_INTERVAL_SECONDS)
    now_with_tz = datetime.now(tz=get_local_timezone())
    delta = threshold - now_with_tz
    if 0 <= delta.total_seconds() <= constants.POLLING_INTERVAL_SECONDS:
        return True
    return False
