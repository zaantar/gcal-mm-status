import settings
from log import log, Level as LogLevel
import calendar_service
import event_parser


def run():
    log('retrieving upcoming events...', LogLevel.INFO)

    test_user = settings.get_user_settings('jan')
    events = calendar_service.get_upcoming_events(test_user)
    log(events, LogLevel.DEBUG)

    log('filtering...', LogLevel.DEBUG)
    tasks = event_parser.events_to_tasks(events, test_user)
    for task in tasks:
        log('Task: "' + task.__str__() + '" needs to perform action: ' + task.action_to_perform().value, LogLevel.INFO)
