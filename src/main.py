import time
from datetime import datetime, timedelta
from log import log, Level as LogLevel
from models.event import Event
from models.task_queue import TaskQueue
import calendar_service
import event_parser
import settings
from constants import constants
from models.user_list import UserList

event_list: [Event] = []
task_queue = TaskQueue()

test_user = None

last_calendar_check = None
last_task_queue_check = None

user_list: UserList = None


def need_check(last_check, interval_seconds):
    if last_check is None:
        return True
    # noinspection PyTypeChecker
    next_check: datetime = last_check + timedelta(seconds=interval_seconds)
    now = datetime.now()
    return next_check < now


def need_calendar_check():
    return need_check(last_calendar_check, constants.CALENDAR_CHECK_POLLING_INTERVAL)


def need_task_queue_check():
    return need_check(last_task_queue_check, constants.TASK_QUEUE_CHECK_INTERVAL)


def update_events():
    global event_list, test_user
    log('Retrieving upcoming events...')
    upcoming_events = calendar_service.get_upcoming_events(test_user)
    log(upcoming_events, LogLevel.DEBUG)

    existing_event_ids = [event.id for event in event_list]
    new_events = [event for event in upcoming_events if event.id not in existing_event_ids]
    log('Filtered new events:')
    log(new_events)

    event_list = event_list + new_events
    # TODO remove old events from the list as well
    return new_events


def load_user_list():
    global user_list
    user_list = UserList([settings.get_user_settings(user_login) for user_login in settings.get_users()])


def main():
    global last_calendar_check, last_task_queue_check, task_queue, test_user, user_list

    load_user_list()
    test_user = user_list.users[0]

    log('Starting the main loop...', LogLevel.DEBUG)
    while True:
        log('Loop iteration at %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogLevel.DEBUG)
        if need_calendar_check():
            log('Checking calendars for new events...')
            new_events = update_events()
            new_tasks = event_parser.events_to_tasks(new_events, test_user)
            for task in new_tasks:
                log(
                    'Task: "' + task.__str__() + '" needs to perform action: ' + task.action_to_perform().value,
                    LogLevel.INFO
                )
            task_queue.add_multiple(new_tasks)
            last_calendar_check = datetime.now()
        else:
            log('Calendar check skipped.')

        if need_task_queue_check():
            ready_tasks = task_queue.pop_ready_tasks()
            log('Printing ready tasks...')
            log(ready_tasks)

            log('Performing actions and rescheduling...')
            for task in ready_tasks:
                task.do_action()
                if Action.WAIT == task.action_to_perform():
                    task_queue.add(task)

            log('All queue tasks:')
            # noinspection PyProtectedMember
            log(task_queue._tasks)
            last_task_queue_check = datetime.now()
        else:
            log('Task queue check skipped.')

        log('Loop iteration completed.', LogLevel.DEBUG)
        time.sleep(10)
