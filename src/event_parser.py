import settings
from task import Task
from dateutil import tz
from dateutil.parser import parse


def events_to_tasks(events, user: settings.UserSettings):
    tasks = []
    for event in events:
        for pattern in user.patterns:
            if pattern.is_match(event['summary']):
                tasks.append(Task(
                    user.mattermost_login,
                    google_date_to_datetime(event['start']),
                    google_date_to_datetime(event['end']),
                    pattern.status,
                    pattern.suffix
                ))
    return tasks


def google_date_to_datetime(google_date):
    dt = parse(google_date['dateTime'])
    if 'timeZone' in google_date:
        event_tz = tz.gettz(google_date['timeZone'])
        dt = dt.replace(tzinfo=event_tz)
    return dt
