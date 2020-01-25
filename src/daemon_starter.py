import daemon
from log import log, set_log_level
from constants.log_level import LogLevel as LogLevel
import signal
import lockfile
import sys


# Needs to be executed with root permissions:
# sudo python3 src/daemon_starter.py

def shutdown(signum, frame):
    log('Shutting down with signal %d' % signum.value)
    sys.exit(0)


def init(preserve_output=False):
    with daemon.DaemonContext(
            stdout=sys.stdout if preserve_output else None,
            stderr=sys.stderr if preserve_output else None,
            stdin=sys.stdin if preserve_output else None,
            signal_map={
                signal.SIGTERM: shutdown,
                signal.SIGTSTP: shutdown,
            },
            pidfile=lockfile.FileLock('/var/run/gcal-mm-status.pid')
    ):
        set_log_level(LogLevel.DEBUG)
        log('Hello world!')
        shutdown(signal.SIGTERM, None)


init(preserve_output=True)
