from __future__ import annotations
from dateutil import tz
from dateutil.parser import parse
from models.user import User
from models.chat_state import ChatState
from constants.mattermost_status import MattermostStatus
from datetime import datetime
import time_utils


class Event:
    """
    Represents an event in a calendar.
    """
    id: str = None
    start: datetime
    end: datetime
    summary = ''
    _is_cancelled: bool
    _is_declined: bool
    _user: User
    _chat_state: ChatState = None

    def __init__(
            self,
            event_id: str,
            start: dict,
            end: dict,
            summary: str,
            user: User,
            is_cancelled: bool = False,
            is_declined: bool = False
    ):
        self.id = event_id
        self.start = Event.google_date_to_datetime(start)
        self.end = Event.google_date_to_datetime(end)
        self.summary = summary
        self._is_cancelled = is_cancelled
        self._is_declined = is_declined
        self._user = user

        self._match_patterns()

    def __str__(self) -> str:
        return self.get_hash()

    def get_user(self) -> User:
        return self._user

    @staticmethod
    def google_date_to_datetime(google_date) -> datetime:
        dt = parse(google_date['dateTime'])
        if 'timeZone' in google_date:
            event_tz = tz.gettz(google_date['timeZone'])
            dt = dt.replace(tzinfo=event_tz)
        return dt

    def _match_patterns(self):
        for pattern in self._user.get_patterns():
            if pattern.is_match(self.summary):
                self._chat_state = ChatState(pattern.suffix, MattermostStatus.from_string(pattern.status))
                break

    def is_actionable(self):
        """
        Determine if this event should produce any tasks.
        """
        return self._chat_state is not None \
            and not self.is_obsolete() \
            and not self._is_cancelled \
            and not self._is_declined

    def get_chat_state(self) -> ChatState:
        return self._chat_state

    def is_same(self, other: Event) -> bool:
        return self.id == other.id and self._user.get_id() == other.get_user().get_id()

    def is_updated_by(self, new_version: Event) -> bool:
        return self.is_same(new_version) and self.get_hash() != new_version.get_hash()

    def get_hash(self) -> str:
        """Produce an unique value representing the whole event and all its relevant properties."""
        chat_state_hash = str(self._chat_state) if self._chat_state is not None else '---'
        return self.id \
            + '|' + str(self.start.timestamp()) \
            + '|' + str(self.end.timestamp()) \
            + '|' + chat_state_hash \
            + '|' + str(self._is_cancelled) \
            + '|' + str(self._is_declined)

    def is_obsolete(self) -> bool:
        return self.end < time_utils.get_now_with_timezone()
