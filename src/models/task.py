from datetime import datetime
from constants.task_action import TaskAction
from controllers.logger import Logger
from controllers.mattermost_service import MattermostService
import time_utils
from models.chat_state import ChatState
from constants.task_type import TaskType


class Task:
    _event_time: datetime
    _user_login: str
    _logger: Logger
    _mattermost_service: MattermostService
    _is_done: bool = False
    _chat_state: ChatState
    _type: TaskType

    def __init__(
            self, event_time: datetime, user_login: str, chat_state: ChatState,
            task_type: TaskType,
            logger: Logger,
            mattermost_service: MattermostService
    ):
        self._event_time = event_time
        self._user_login = user_login
        self._chat_state = chat_state
        self._type = task_type
        self._logger = logger
        self._mattermost_service = mattermost_service

    def __str__(self) -> str:
        return "{%s -> %s @ %s}" % (
            self._user_login, str(self._chat_state), self._event_time.strftime('%Y-%m-%d %H:%M')
        )

    def is_ready(self):
        return self._event_time <= time_utils.get_now_with_timezone()

    def action_to_perform(self):
        if self._is_done:
            return TaskAction.REMOVE
        elif self.is_ready():
            return TaskAction.START
        return TaskAction.WAIT

    def do_action(self):
        if TaskAction.START != self.action_to_perform():
            self._logger.warning('%s: There is no action to perform' % str(self))
            return

        self._logger.info('Performing task %s...' % str(self), 1)
        self._chat_state.apply(self._user_login, self._mattermost_service)
        self._is_done = True
        self._logger.untab()

    def get_event_time(self) -> datetime:
        return self._event_time

    def get_type(self) -> TaskType:
        return self._type
