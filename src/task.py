from enum import Enum


class Action(Enum):
    START = 'start'
    FINISH = 'finish'


class Task:
    user_login = ''
    start_time = None
    end_time = None
    status = ''
    suffix = ''
    was_started = False
    was_completed = False

    def __init__(self, user_login, start_time, end_time, status, suffix):
        self.user_login = user_login
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.suffix = suffix
        return

    def __str__(self) -> str:
        return "For %s set status %s and suffix %s between %s and %s." % (
            self.user_login, self.status, self.suffix, self.start_time, self.end_time
        )

    def needs_to_start(self):
        return False

    def needs_to_finish(self):
        return False

    def action_to_perform(self):
        if self.needs_to_start() and not self.was_started:
            return Action.START
        if self.needs_to_finish() and not self.was_completed:
            return Action.FINISH
        return None

    def is_actionable(self):
        return self.action_to_perform() is not None
