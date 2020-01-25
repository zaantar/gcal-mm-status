import models.user_settings
import settings
from models.task import Task
from models.event import Event
from constants.mattermost_status import MattermostStatus


def events_to_tasks(events: [Event], user: models.user_settings.UserSettings):
    tasks = []
    for event in events:
        for pattern in user.patterns:
            if pattern.is_match(event.summary):
                new_task = Task(
                    user.mattermost_login,
                    event.start,
                    event.end,
                    get_status_from_string(pattern.status),
                    pattern.suffix
                )
                event.add_task(new_task)
                tasks.append(new_task)
    for i in range(1, len(tasks)):
        current_task = tasks[i]
        previous_task = tasks[i - 1]

        if current_task.start_time <= previous_task.end_time <= current_task.end_time:
            previous_task.is_end_overlapping = True

    return tasks


def get_status_from_string(status_str):
    if status_str not in MattermostStatus:
        return MattermostStatus.ONLINE
    return MattermostStatus[status_str]
