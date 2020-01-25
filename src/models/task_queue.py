from constants.mattermost_status import MattermostStatus
from constants.log_level import LogLevel

from models.task import Task, Action
from models.event import Event

from controllers.logger import Logger
from controllers.mattermost_service import MattermostService

def get_task_comparison_key(task: Task):
    if not task.was_started:
        return task.start_time
    return task.end_time


def get_status_from_string(status_str):
    if status_str not in MattermostStatus:
        return MattermostStatus.ONLINE
    return MattermostStatus[status_str]


class TaskQueue:
    _tasks: [Task] = []
    _logger: Logger
    _mattermost_service: MattermostService

    def __init__(self, logger: Logger, mattermost_service: MattermostService):
        self._logger = logger
        self._mattermost_service = mattermost_service

    def _sort(self):
        self._tasks.sort(key=get_task_comparison_key)

    def add(self, task: Task, update_overlaps=True):
        self._tasks.append(task)
        if update_overlaps:
            self.update_overlaps()

    def pop_ready_tasks(self):
        self._sort()
        ready_tasks = []
        while self._tasks[0].is_actionable():
            task = self._tasks.pop(0)
            action = task.action_to_perform()
            if Action.REMOVE == action:
                continue
            ready_tasks.append(task)
        return ready_tasks

    def add_from_events(self, events: [Event]):
        for event in events:
            user = event.get_user()
            for pattern in user.patterns:
                if pattern.is_match(event.summary):
                    new_task = Task(
                        user.mattermost_login,
                        event.start,
                        event.end,
                        get_status_from_string(pattern.status),
                        pattern.suffix,
                        self._mattermost_service
                    )
                    event.add_task(new_task)
                    self.add(new_task, update_overlaps=False)
                    self._logger.log(
                        'New task: "' + new_task.__str__()
                        + '" needs to perform action: ' + new_task.action_to_perform().value,
                        LogLevel.INFO
                    )
        self.update_overlaps()

    def update_overlaps(self):
        for i in range(1, len(self._tasks)):
            current_task = self._tasks[i]
            previous_task = self._tasks[i - 1]

            if current_task.start_time <= previous_task.end_time <= current_task.end_time:
                previous_task.is_end_overlapping = True
