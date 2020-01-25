from dateutil import tz
from dateutil.parser import parse
from models.task import Task


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

    def __init__(self, id, start, end, summary, is_cancelled=False):
        self.id = id
        self.start = google_date_to_datetime(start)
        self.end = google_date_to_datetime(end)
        self.summary = summary
        self.is_cancelled = is_cancelled

    def add_task(self, task: Task):
        self.tasks.append(task)

    def __str__(self) -> str:
        return "Event #%s from %s to %s: '%s'" % (
            self.id, self.start, self.end, self.summary
        )
