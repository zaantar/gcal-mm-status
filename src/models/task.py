from datetime import datetime
from constants.task_action import TaskAction
from controllers.logger import Logger
from controllers.mattermost_service import MattermostService
import time_utils
from models.chat_state import ChatState
from constants.task_type import TaskType


class Task:
    """
    Single task - one thing that should be done at one particular time, which can be either a beginning or
    an end of a calendar event.
    """
    _event_time: datetime
    _user_login: str
    _logger: Logger
    _mattermost_service: MattermostService
    _is_done: bool = False
    _chat_state: ChatState
    _type: TaskType

    def __init__(
            self,
            event_time: datetime,
            user_login: str,
            chat_state: ChatState,
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
        return "{%s -> %s @ %s%s}" % (
            self._user_login,
            str(self._chat_state),
            self._event_time.strftime('%Y-%m-%d %H:%M'),
            ' (done)' if self._is_done else ''
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
        """
        If the task is ready, apply the chat state.
        """
        if TaskAction.START != self.action_to_perform():
            self._logger.warning('%s: There is no action to perform' % str(self))
            return

        self._logger.info('Performing task %s...' % str(self), 1)
        is_chat_state_applied = self._chat_state.apply(self._user_login, self._mattermost_service)
        if not is_chat_state_applied:
            self._logger.error('Task could not have been performed successfully. Will attempt again.')
            # todo attempt only a limited amount of attempts
        self._is_done = is_chat_state_applied
        self._logger.untab()

    def get_event_time(self) -> datetime:
        return self._event_time

    def get_type(self) -> TaskType:
        return self._type

    def get_user_login(self) -> str:
        return self._user_login

    def set_as_done(self):
        self._is_done = True
