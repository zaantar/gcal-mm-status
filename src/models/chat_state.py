from constants.mattermost_status import MattermostStatus
from controllers.mattermost_service import MattermostService


class ChatState:
    _suffix: str
    _status: MattermostStatus

    def __init__(self, suffix: str, status: MattermostStatus):
        self._suffix = suffix
        self._status = status

    def __str__(self) -> str:
        return '%s | %s' % (self._suffix, self._status.name)

    def apply(self, user_login: str, mattermost_service: MattermostService):
        mattermost_service.set_user_status(user_login, self._status)
        mattermost_service.set_user_suffix(user_login, self._suffix)