from __future__ import annotations

from enum import Enum
from datetime import datetime
from constants.mattermost_status import MattermostStatus
import time_utils
from controllers.mattermost_service import MattermostService
from constants import constants
from controllers.logger import Logger
from constants.log_level import LogLevel


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
    _is_end_overlapping_exactly = False
    suffix_to_restore = ''
    _mattermost_service: MattermostService
    _logger: Logger
    _overlapping_task: Task | None = None

    def __init__(
            self,
            user_login,
            start_time: datetime,
            end_time: datetime,
            status: MattermostStatus,
            suffix,
            mattermost_service: MattermostService,
            logger: Logger
    ):
        self.user_login = user_login
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.suffix = suffix
        self._mattermost_service = mattermost_service
        self._logger = logger

    def __str__(self) -> str:
        return "{%s -> %s | %s ~ (%s - %s)}" % (
            self.user_login, self.status, self.suffix, self.start_time.strftime('%Y-%m-%d %H:%M'),
            self.end_time.strftime('%Y-%m-%d %H:%M')
        )

    def needs_to_start_now(self):
        return time_utils.is_in_time_range(self.start_time, constants.TASK_QUEUE_CHECK_INTERVAL * 2)

    def needs_to_finish_now(self):
        return self.end_time <= time_utils.get_now_with_timezone()

    def has_missed_start(self):
        return time_utils.is_after_threshold(self.start_time, constants.TASK_QUEUE_CHECK_INTERVAL)

    def action_to_perform(self):
        if not self.was_started:
            if self.needs_to_start_now():
                return Action.START
            elif self.has_missed_start():
                # this is possible only when starting the service while an event is already ongoing
                self._logger.log('Detected a missed start for ' + str(self), LogLevel.WARNING)
                return Action.START
            return Action.WAIT

        if not self.was_completed:
            if self.needs_to_finish_now():
                if self._is_end_overlapping_exactly:
                    self._logger.debug(
                        'The end of the task %s is overlapping exactly with %s - voting for removal.' % (
                            str(self), str(self._overlapping_task)
                        )
                    )
                    return Action.REMOVE
                return Action.FINISH
            return Action.WAIT

        return Action.REMOVE

    def is_actionable(self):
        return self.action_to_perform() != Action.WAIT

    def do_action(self):
        action = self.action_to_perform()
        self._logger.log('Action %s for task %s...' % (action.name, str(self)), LogLevel.INFO, 1)
        if Action.START == action:
            self.suffix_to_restore = self._mattermost_service.get_user_suffix(self.user_login)
            self._mattermost_service.set_user_status(self.user_login, self.status)
            self._mattermost_service.set_user_suffix(self.user_login, self.suffix)
            self.was_started = True
        elif Action.FINISH == action:
            if self._overlapping_task is not None:
                self._mattermost_service.set_user_status(self.user_login, self._overlapping_task.status)
                self._mattermost_service.set_user_suffix(self.user_login, self._overlapping_task.suffix)
            else:
                self._mattermost_service.set_user_status(self.user_login, MattermostStatus.OFFLINE)
                self._mattermost_service.set_user_suffix(self.user_login, 'off')
            self.was_completed = True
        self._logger.untab()

    def add_overlapping_task(self, overlapping_task: Task):
        self._overlapping_task = overlapping_task
        if self.end_time == overlapping_task.start_time:
            self._is_end_overlapping_exactly = True
