from models.event import Event
from models.user_list import UserList

from log import log
from constants.log_level import LogLevel as LogLevel
import calendar_service


class EventList:
    _events: [Event] = []
    _users: UserList = None

    def __init__(self, user_list: UserList):
        self._users = user_list

    def fetch_new_events(self):
        log('Retrieving upcoming events...')
        # todo fetch from all users
        upcoming_events = calendar_service.get_upcoming_events(self._users.users[0])
        log(upcoming_events, LogLevel.DEBUG)

        existing_event_ids = [event.id for event in self._events]
        new_events = [event for event in upcoming_events if event.id not in existing_event_ids]
        log('Filtered new events:')
        log(new_events)

        self._events = self._events + new_events
        # TODO remove old events from the list as well
        return new_events
