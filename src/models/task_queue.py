from models.task import Task
from constants.task_action import TaskAction

from controllers.logger import Logger
from controllers.mattermost_service import MattermostService


class TaskQueue:
    """Queue of upcoming tasks."""
    _tasks: [Task] = []
    _logger: Logger
    _mattermost_service: MattermostService

    def __init__(self, logger: Logger, mattermost_service: MattermostService):
        self._logger = logger
        self._mattermost_service = mattermost_service

    def add(self, task: Task):
        """Add one new task to the queue."""
        self._tasks.append(task)

    def set(self, tasks: [Task]):
        """Overwrite the whole queue with a new set of tasks."""
        self._tasks = tasks

    def get_ready_tasks(self):
        """
        Get up to one task for each user that is ready to be performed.

        Also clean the queue from tasks that request to be removed.
        """
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
