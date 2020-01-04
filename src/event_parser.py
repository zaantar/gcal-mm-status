import settings
from task import Task


def events_to_tasks(events, user: settings.UserSettings):
    tasks = []
    for event in events:
        for pattern in user.patterns:
            if pattern.is_match(event['summary']):
                tasks.append(Task(user.mattermost_login, event['start'], event['end'], pattern.status, pattern.suffix))
    return tasks
