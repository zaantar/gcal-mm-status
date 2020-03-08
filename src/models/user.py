from typing import List
from models.chat_state import ChatState
from models.event_pattern import EventPattern
from constants.mattermost_status import MattermostStatus


class User:
    """
    Represents a single user, identified by its Mattermost username.
    """
    _mattermost_login = ''
    _gcal_token_file = ''
    _patterns: List[EventPattern] = []
    _id: str
    _default_chat_state: ChatState

    def __init__(self, user_settings):
        self._mattermost_login = user_settings['mattermost_login']
        self._gcal_token_file = user_settings['gcal_token_file']
        for pattern_settings in user_settings['patterns']:
            self._patterns.append(EventPattern(pattern_settings))
        self._id = self._mattermost_login
        self._default_chat_state = ChatState(
            user_settings['default_chat_state']['suffix'],
            MattermostStatus.from_string(user_settings['default_chat_state']['status'])
        )

    def get_id(self):
        return self._id

    def get_patterns(self) -> [EventPattern]:
        return self._patterns

    def get_default_chat_state(self) -> ChatState:
        return self._default_chat_state

    def get_mattermost_login(self) -> str:
        return self._mattermost_login

    def get_gcal_token_file_name(self) -> str:
        return self._gcal_token_file
