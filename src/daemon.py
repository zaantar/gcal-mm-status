import settings
import log


def run():
    log.l('the daemon has been executed', log.Level.INFO)
    log.l(settings.get_setting('testSetting'), log.Level.DEBUG)
