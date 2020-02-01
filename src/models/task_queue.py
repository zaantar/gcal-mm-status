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

    def get_ready_tasks(self):
        self._tasks.sort(key=lambda current_task: current_task.get_event_time())
        for task in self._tasks:
            if task.action_to_perform() == TaskAction.REMOVE:
                self._logger.debug('Removing a completed task %s.' % str(task))
                self._tasks.remove(task)

        ready_tasks = [task for task in self._tasks if task.action_to_perform() == TaskAction.START]

        # For each user, return only a single task
        users_with_ready_tasks = set([task.get_user_login() for task in ready_tasks])
        selected_tasks: [Task] = []
        for user_login in users_with_ready_tasks:
            tasks_for_user = [task for task in ready_tasks if task.get_user_login() == user_login]
            tasks_for_user.sort(key=lambda current_task: current_task.get_event_time(), reverse=True)
            selected_tasks.append(tasks_for_user[0])

            for task in tasks_for_user[1:]:
                # If we don't do this, the task may be executed later
                task.set_as_done()

        return selected_tasks
