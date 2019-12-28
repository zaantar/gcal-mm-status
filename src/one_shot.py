import settings
import log
import calendar_service
import event_filter


def run():
    log.l('the daemon has been executed', log.Level.INFO)
    log.l(settings.get_setting('testSetting'), log.Level.DEBUG)
    log.l('retrieving upcoming events...', log.Level.INFO)

    events = calendar_service.get_upcoming_events()
    log.l(events, log.Level.DEBUG)

    log.l('filtering...', log.Level.DEBUG)
    filtered_events = event_filter.filter_events(events)
    log.l(filtered_events, log.Level.DEBUG)
