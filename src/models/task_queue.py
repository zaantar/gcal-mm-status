from models.task import Task
from constants.task_action import TaskAction

from controllers.logger import Logger
from controllers.mattermost_service import MattermostService


class TaskQueue:
    _tasks: [Task] = []
    _logger: Logger
    _mattermost_service: MattermostService

    def __init__(self, logger: Logger, mattermost_service: MattermostService):
        self._logger = logger
        self._mattermost_service = mattermost_service

    def add(self, task: Task):
        self._tasks.append(task)

    def set(self, tasks: [Task]):
        self._tasks = tasks

    def pop_ready_tasks(self):
        self._tasks.sort(key=lambda current_task: current_task.get_event_time())
        for task in self._tasks:
            if task.action_to_perform() == TaskAction.REMOVE:
                self._logger.debug('Removing a completed task %s.' % str(task))
                self._tasks.remove(task)

        return [task for task in self._tasks if task.action_to_perform() == TaskAction.START]
