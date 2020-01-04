from enum import Enum
from datetime import datetime
import time_utils


class Action(Enum):
    START = 'start'
    FINISH = 'finish'
    NONE = 'none'


class Task:
    user_login = ''
    start_time: datetime = None
    end_time: datetime = None
    status = ''
    suffix = ''
    was_started = False
    was_completed = False
    is_end_overlapping = False

    def __init__(self, user_login, start_time, end_time, status, suffix):
        self.user_login = user_login
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.suffix = suffix
        return

    def __str__(self) -> str:
        return "for %s set status %s and suffix %s between %s and %s." % (
            self.user_login, self.status, self.suffix, self.start_time, self.end_time
        )

    def needs_to_start(self):
        return time_utils.is_in_time_range(self.start_time)

    def needs_to_finish(self):
        return time_utils.is_in_time_range(self.end_time)

    def action_to_perform(self):
        if self.needs_to_start() and not self.was_started:
            return Action.START
        if self.was_started \
                and self.needs_to_finish() \
                and not self.was_completed \
                and not self.is_end_overlapping:
            return Action.FINISH
        return Action.NONE

    def is_actionable(self):
        return self.action_to_perform() is not None
