from models.event import Event
from models.user_list import UserList
from constants.log_level import LogLevel as LogLevel
from controllers.calendar_service import CalendarService
from controllers.logger import Logger
from constants.task_type import TaskType
from models.task import Task
from controllers.mattermost_service import MattermostService
from models.chat_state import ChatState
from constants.mattermost_status import MattermostStatus
from models.user import User


class EventList:
    _events: [Event] = []
    _users: UserList
    _calendar_service: CalendarService
    _logger: Logger
    _mattermost_service: MattermostService

    def __init__(self, user_list: UserList, calendar_service: CalendarService, logger: Logger,
                 mattermost_service: MattermostService):
        self._users = user_list
        self._calendar_service = calendar_service
        self._logger = logger
        self._mattermost_service = mattermost_service

    def fetch_new_events(self):
        upcoming_events = []
        for user in self._users.get_users():
            self._logger.log('Retrieving upcoming events for user %s...' % user.mattermost_login)
            upcoming_user_events = self._calendar_service.get_upcoming_events(user)
            self._logger.log(upcoming_user_events, LogLevel.DEBUG)
            upcoming_events = upcoming_events + upcoming_user_events

        existing_event_ids = [event.id for event in self._events]
        new_events = [event for event in upcoming_events if
                      event.id not in existing_event_ids and event.is_actionable()]
        self._events = self._events + new_events
        # TODO remove old events from the list as well

        self._logger.log('Filtered new events:')
        self._logger.log(new_events)

        return new_events

    def build_tasks(self):
        all_tasks: [Task] = []
        for user in self._users.get_users():
            all_tasks = all_tasks + self._build_task_per_user(user)
        return all_tasks

    def _build_task_per_user(self, user: User):
        user_events = [
            event
            for event in self._events
            if event.get_user().mattermost_login == user.mattermost_login
        ]

        state_changes = \
            [
                {'type': TaskType.START, 'event': event, 'time': event.start}
                for event in user_events
            ] + [
                {'type': TaskType.END, 'event': event, 'time': event.end}
                for event in user_events
            ]
        state_changes.sort(key=lambda change: change['time'])

        started_events: [Event] = []
        all_tasks: [Task] = []

        for state_change in state_changes:
            if state_change['type'] == TaskType.START:
                all_tasks.append(Task(
                    state_change['time'],
                    user.mattermost_login,
                    state_change['event'].get_chat_state(),
                    TaskType.START,
                    self._logger,
                    self._mattermost_service
                ))
                started_events.append(state_change['event'])
            else:
                started_events_except_current = [event for event in started_events if
                                                 event != state_change['event']]
                started_events_except_current.sort(key=lambda event: event.start, reverse=True)
                chat_state: ChatState
                if len(started_events_except_current) == 0:
                    # TODO store this default in the user object
                    chat_state = ChatState('off', MattermostStatus.OFFLINE)
                else:
                    latest_overlapping_event: Event = started_events_except_current[0]
                    chat_state = latest_overlapping_event.get_chat_state()

                all_tasks.append(Task(
                    state_change['time'],
                    user.mattermost_login,
                    chat_state,
                    TaskType.END,
                    self._logger,
                    self._mattermost_service
                ))
                started_events.remove(state_change['event'])

        non_overlapping_tasks: [Task] = []
        task_times = set([task.get_event_time() for task in all_tasks])

        def task_type_to_sort_key(task: Task):
            if task.get_type() == TaskType.START:
                return 0
            return 1

        for current_task_time in task_times:
            same_time_tasks = [
                task for task in all_tasks if task.get_event_time() == current_task_time
            ]
            same_time_tasks.sort(key=task_type_to_sort_key)
            non_overlapping_tasks.append(same_time_tasks[0])

        return non_overlapping_tasks
