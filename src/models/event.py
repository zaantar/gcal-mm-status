from dateutil import tz
from dateutil.parser import parse
from models.task import Task
from models.user_settings import UserSettings


def google_date_to_datetime(google_date):
    dt = parse(google_date['dateTime'])
    if 'timeZone' in google_date:
        event_tz = tz.gettz(google_date['timeZone'])
        dt = dt.replace(tzinfo=event_tz)
    return dt


class Event:
    id = None
    start = None
    end = None
    summary = ''
    is_cancelled = False
    tasks = []
    _user: UserSettings

    def __init__(self, event_id, start, end, summary, user: UserSettings, is_cancelled=False):
        self.id = event_id
        self.start = google_date_to_datetime(start)
        self.end = google_date_to_datetime(end)
        self.summary = summary
        self.is_cancelled = is_cancelled
        self._user = user

    def __str__(self) -> str:
        return "Event #%s from %s to %s: '%s'" % (
            self.id, self.start, self.end, self.summary
        )

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_user(self):
        return self._user
