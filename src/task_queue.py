from task import Task, Action


def get_task_comparison_key(task: Task):
    if not task.was_started:
        return task.start_time
    return task.end_time


class TaskQueue:
    _tasks = []

    def _sort(self):
        self._tasks.sort(key=get_task_comparison_key)

    def add(self, task: Task):
        self._tasks.append(task)

    def add_multiple(self, tasks: [Task]):
        for task in tasks:
            self._tasks.append(task)

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
