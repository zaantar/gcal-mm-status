import time
from datetime import datetime, timedelta
from constants.log_level import LogLevel as LogLevel
from models.task_queue import TaskQueue
import settings
from constants import constants
from models.user_list import UserList
from controllers.event_list import EventList
from controllers.logger import Logger
from controllers.calendar_service import CalendarService

logger: Logger = Logger()
task_queue: TaskQueue = TaskQueue(logger)

last_calendar_check = None
last_task_queue_check = None

user_list: UserList
event_list: EventList


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


def log(message, level: LogLevel = LogLevel.INFO):
    global logger
    logger.log(message, level)


def main():
    global last_calendar_check, last_task_queue_check, task_queue, user_list, event_list, logger

    user_list = UserList([settings.get_user_settings(user_login) for user_login in settings.get_users()])
    calendar_service = CalendarService(logger)
    event_list = EventList(user_list, calendar_service, logger)

    log('Starting the main loop...', LogLevel.DEBUG)
    while True:
        log('Loop iteration at %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'), LogLevel.DEBUG)
        if need_calendar_check():
            log('Checking calendars for new events...')
            task_queue.add_from_events(event_list.fetch_new_events())
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
