from enum import Enum
from datetime import datetime

from constants.mattermost_status import MattermostStatus
import time_utils
import mattermost_service
from constants import constants


class Action(Enum):
    START = 'start'
    FINISH = 'finish'
    WAIT = 'wait'
    REMOVE = 'remove'


class Task:
    user_login = ''
    start_time: datetime = None
    end_time: datetime = None
    status: MattermostStatus = None
    suffix = ''
    was_started = False
    was_completed = False
    is_end_overlapping = False
    suffix_to_restore = ''

    def __init__(self, user_login, start_time: datetime, end_time: datetime, status: MattermostStatus, suffix):
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
        return time_utils.is_in_time_range(self.start_time, constants.TASK_QUEUE_CHECK_INTERVAL)

    def needs_to_finish(self):
        return (
                time_utils.is_in_time_range(self.end_time, constants.TASK_QUEUE_CHECK_INTERVAL)
                and not self.is_end_overlapping
        )

    def has_missed_start(self):
        return time_utils.is_after_threshold(self.start_time, constants.TASK_QUEUE_CHECK_INTERVAL)

    def action_to_perform(self):
        if not self.was_started:
            if self.needs_to_start():
                return Action.START
            elif self.has_missed_start():
                return Action.REMOVE
            return Action.WAIT

        if not self.was_completed:
            if self.needs_to_finish():
                return Action.FINISH
            return Action.WAIT

        return Action.REMOVE

    def is_actionable(self):
        return self.action_to_perform() != Action.WAIT

    def do_action(self):
        action = self.action_to_perform()
        if Action.START == action:
            self.suffix_to_restore = mattermost_service.get_user_suffix(self.user_login)
            mattermost_service.set_user_status(self.user_login, self.status)
            mattermost_service.set_user_suffix(self.user_login, self.suffix)
            self.was_started = True
        elif Action.FINISH == action:
            mattermost_service.set_user_status(self.user_login, MattermostStatus.OFFLINE)
            mattermost_service.set_user_suffix(self.user_login, self.suffix_to_restore)
            self.was_completed = True
