from dateutil import tz
from dateutil.parser import parse
from models.user_settings import UserSettings
from models.chat_state import ChatState
from constants.mattermost_status import MattermostStatus
from datetime import datetime


def google_date_to_datetime(google_date) -> datetime:
    dt = parse(google_date['dateTime'])
    if 'timeZone' in google_date:
        event_tz = tz.gettz(google_date['timeZone'])
        dt = dt.replace(tzinfo=event_tz)
    return dt


def get_status_from_string(status_str) -> MattermostStatus:
    try:
        return MattermostStatus(status_str)
    except ValueError:
        return MattermostStatus.ONLINE


class Event:
    id = None
    start: datetime
    end: datetime
    summary = ''
    is_cancelled = False
    _user: UserSettings
    _chat_state: ChatState

    def __init__(self, event_id, start, end, summary, user: UserSettings, is_cancelled=False):
        self.id = event_id
        self.start = google_date_to_datetime(start)
        self.end = google_date_to_datetime(end)
        self.summary = summary
        self.is_cancelled = is_cancelled
        self._user = user

        self._match_patterns()

    def __str__(self) -> str:
        return "Event #%s from %s to %s: '%s'" % (
            self.id, self.start, self.end, self.summary
        )

    def get_user(self) -> UserSettings:
        return self._user

    def _match_patterns(self):
        for pattern in self._user.patterns:
            if pattern.is_match(self.summary):
                self._chat_state = ChatState(pattern.suffix, get_status_from_string(pattern.status))
                break

    def is_actionable(self):
        return self._chat_state is not None

    def get_chat_state(self) -> ChatState:
        return self._chat_state
