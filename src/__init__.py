import log
import sys
from main import main

if not sys.version_info.major == 3 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
    print('This software requires Python 3 from the version 3.6 or above.')

log.set_log_level(log.Level.DEBUG)
main()
