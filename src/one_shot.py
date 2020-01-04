import settings
import log
import calendar_service
import event_parser


def run():
    log.l('retrieving upcoming events...', log.Level.INFO)

    test_user = settings.get_user_settings('jan')
    events = calendar_service.get_upcoming_events(test_user)
    log.l(events, log.Level.DEBUG)

    log.l('filtering...', log.Level.DEBUG)
    tasks = event_parser.events_to_tasks(events, test_user)
    log.l(tasks, log.Level.DEBUG)
