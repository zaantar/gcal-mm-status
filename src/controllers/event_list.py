from models.event import Event
from models.user_list import UserList
from constants.log_level import LogLevel as LogLevel
from controllers.calendar_service import CalendarService
from controllers.logger import Logger


class EventList:
    _events: [Event] = []
    _users: UserList
    _calendar_service: CalendarService
    _logger: Logger

    def __init__(self, user_list: UserList, calendar_service: CalendarService, logger: Logger):
        self._users = user_list
        self._calendar_service = calendar_service
        self._logger = logger

    def fetch_new_events(self):
        upcoming_events = []
        for user in self._users.get_users():
            self._logger.log('Retrieving upcoming events for user %s...' % user.mattermost_login)
            upcoming_user_events = self._calendar_service.get_upcoming_events(user)
            self._logger.log(upcoming_user_events, LogLevel.DEBUG)
            upcoming_events = upcoming_events + upcoming_user_events

        existing_event_ids = [event.id for event in self._events]
        new_events = [event for event in upcoming_events if event.id not in existing_event_ids]
        self._events = self._events + new_events
        # TODO remove old events from the list as well

        self._logger.log('Filtered new events:')
        self._logger.log(new_events)

        return new_events
