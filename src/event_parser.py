import settings
from task import Task
from dateutil import tz
from dateutil.parser import parse
from mattermost_service import Status


def events_to_tasks(events, user: settings.UserSettings):
    tasks = []
    for event in events:
        for pattern in user.patterns:
            if pattern.is_match(event['summary']):
                tasks.append(Task(
                    user.mattermost_login,
                    google_date_to_datetime(event['start']),
                    google_date_to_datetime(event['end']),
                    get_status_from_string(pattern.status),
                    pattern.suffix
                ))
    for i in range(1, len(tasks)):
        current_task = tasks[i]
        previous_task = tasks[i - 1]

        if current_task.start_time <= previous_task.end_time <= current_task.end_time:
            previous_task.is_end_overlapping = True

    return tasks


def get_status_from_string(status_str):
    if status_str not in Status:
        return Status.ONLINE
    return Status[status_str]


def google_date_to_datetime(google_date):
    dt = parse(google_date['dateTime'])
    if 'timeZone' in google_date:
        event_tz = tz.gettz(google_date['timeZone'])
        dt = dt.replace(tzinfo=event_tz)
    return dt
