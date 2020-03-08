"""Main application file, with the program loop."""
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
from controllers.mattermost_service import MattermostService
from models.task import Task

logger: Logger = Logger()
mattermost_service = MattermostService(logger)
task_queue: TaskQueue = TaskQueue(logger, mattermost_service)

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


def main():
    global last_calendar_check, last_task_queue_check, task_queue, user_list, event_list, logger

    user_list = UserList([settings.get_user_settings(user_login) for user_login in settings.get_users()])
    calendar_service = CalendarService(logger)
    event_list = EventList(user_list, calendar_service, logger, mattermost_service)

    logger.set_level_threshold(LogLevel.DEBUG)
    logger.log('Starting the main loop...', LogLevel.DEBUG)

    while True:
        logger.log('Loop iteration', LogLevel.DEBUG, 1)
        if need_calendar_check():
            logger.log('Checking calendars for new events...', LogLevel.INFO, 1)
            has_updates = event_list.update_events()
            if has_updates:
                all_tasks = event_list.build_tasks()
                task_queue.set(all_tasks)
            last_calendar_check = datetime.now()
            logger.untab()
        else:
            logger.log('Calendar check skipped.', LogLevel.DEBUG)

        if need_task_queue_check():
            logger.debug('Checking ready tasks...', 1)
            ready_tasks = task_queue.get_ready_tasks()
            if len(ready_tasks) > 0:
                logger.debug(ready_tasks)
                logger.log('Executing tasks...', LogLevel.DEBUG)
                task: Task
                for task in ready_tasks:
                    logger.info('Task ' + str(task) + '...', 1)
                    task.do_action()
                    logger.untab()
            else:
                logger.debug('No tasks are ready to be executed.')
            # noinspection PyProtectedMember
            logger.debug("All queue tasks: \n%s" % logger.stringify(task_queue._tasks))
            logger.untab()
            last_task_queue_check = datetime.now()
        else:
            logger.log('Task queue check skipped.', LogLevel.DEBUG)

        logger.log('Loop iteration completed.', LogLevel.DEBUG, -1)
        time.sleep(20)
