from models.event import Event
from models.user_list import UserList
from constants.log_level import LogLevel as LogLevel
from controllers.calendar_service import CalendarService
from controllers.logger import Logger
from constants.task_type import TaskType
from models.task import Task
from controllers.mattermost_service import MattermostService
from models.chat_state import ChatState
from models.user import User


class EventList:
    """
    Maintains the list of events for all users and processes it into actionable tasks.
    """
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

    def update_events(self) -> bool:
        """
        Fetch new and updated upcoming events for all users.

        :return: Whether there have been any changes in the event list.
        """
        upcoming_events = []
        user: User
        has_updates = False

        # Fetch new events for all users.
        for user in self._users.get_users():
            self._logger.log('Retrieving upcoming events for user %s...' % user.get_mattermost_login())
            upcoming_user_events = self._calendar_service.get_upcoming_events(user)
            self._logger.debug("Retrieved upcoming events: \n%s" % self._logger.stringify(upcoming_user_events))
            upcoming_events = upcoming_events + upcoming_user_events

        # Extract new events that aren't already in the list.
        # If an event already exists but has been updated in Google Calendar, also update it in the list.
        new_events: [Event] = []
        for new_event in upcoming_events:
            found = False
            old_event: Event
            for old_event in self._events:
                if old_event.is_same(new_event):
                    if old_event.is_updated_by(new_event):
                        self._events.remove(old_event)
                        self._events.append(new_event)
                        self._logger.info('Event %s has been updated by %s.' % (str(old_event), str(new_event)))
                        has_updates = True
                    else:
                        self._logger.debug('Skipping event %s, it is already in the list.' % str(new_event))
                    found = True
                    break
            if not found:
                new_events.append(new_event)
                has_updates = True

        # Append new events to the list and log them.
        self._events: [Event] = self._events + new_events
        self._logger.info("New events:\n" + self._logger.stringify(new_events))

        # Remove all obsolete events.
        for event in self._events:
            if event.is_obsolete():
                self._logger.info('Removing obsolete event %s from the list.' % str(event))
                self._events.remove(event)
                has_updates = True

        return has_updates

    def build_tasks(self) -> [Task]:
        """
        Build the complete, properly sorted list of tasks from events.
        :return: List of tasks sorted by time in ascending order.
        """
        all_tasks: [Task] = []
        for user in self._users.get_users():
            all_tasks = all_tasks + self._build_task_per_user(user)
        all_tasks.sort(key=lambda task: task.get_event_time())
        return all_tasks

    def _build_task_per_user(self, user: User) -> [Task]:
        """
        Build the list of tasks from events for a given user.
        :param user:
        :return:
        """
        # Filter out events that belong to the given user.
        user_events = [
            event
            for event in self._events
            if event.get_user().get_id() == user.get_id()
        ]

        # Ignore non-actionable stuff.
        actionable_events = [event for event in user_events if event.is_actionable()]

        # Find out all the times where the user's chat state should change (in any way).
        # This will be important to determine overlapping tasks and chat state transitions.
        state_changes = \
            [
                {'type': TaskType.START, 'event': event, 'time': event.start}
                for event in actionable_events
            ] + [
                {'type': TaskType.END, 'event': event, 'time': event.end}
                for event in actionable_events
            ]
        state_changes.sort(key=lambda change: change['time'])

        # This will hold events whose start has been already processed in the for cycle below, but not the end.
        started_events: [Event] = []
        all_tasks: [Task] = []

        for state_change in state_changes:
            if state_change['type'] == TaskType.START:
                # When an event starts, the situation is straightforward: Create a task to
                # update the chat state at that time.
                all_tasks.append(Task(
                    state_change['time'],
                    user.get_mattermost_login(),
                    state_change['event'].get_chat_state(),
                    TaskType.START,
                    self._logger,
                    self._mattermost_service
                ))
                # Remember that we've processed the beginning.
                started_events.append(state_change['event'])
            else:
                # An end of an event. We must determine the chat state _after_ the event,
                # which may either be the state of an event that has been started previously but finishes later
                # than the current one (the current event is being encompassed by it) or the
                # default chat state.
                started_events_except_current = [event for event in started_events if
                                                 event != state_change['event']]
                started_events_except_current.sort(key=lambda event: event.start, reverse=True)
                chat_state: ChatState
                if len(started_events_except_current) == 0:
                    # There are no encompassing events.
                    chat_state = user.get_default_chat_state()
                else:
                    # Get the chat state from the latest encompassing event. This may not be exactly
                    # what the user intends but we can't do much better without additional information.
                    latest_overlapping_event: Event = started_events_except_current[0]
                    chat_state = latest_overlapping_event.get_chat_state()

                all_tasks.append(Task(
                    state_change['time'],
                    user.get_mattermost_login(),
                    chat_state,
                    TaskType.END,
                    self._logger,
                    self._mattermost_service
                ))

                # Note that this event's processing has been finished.
                started_events.remove(state_change['event'])

        # Finally, find _tasks_ that are supposed to happen at the same time and choose only one.
        # Event start is always preferred over event end, and we always take the first from those
        # (it's an arbitrary choice, but we can't do better without having more information.)
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
