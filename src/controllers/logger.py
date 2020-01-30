from constants.log_level import LogLevel
from datetime import datetime


class Logger:
    _level_threshold: LogLevel
    _indentation: int = 0

    def __init__(self, level_threshold: LogLevel = LogLevel.INFO):
        self._level_threshold = level_threshold

    def set_level_threshold(self, new_threshold: LogLevel):
        self._level_threshold = new_threshold

    @staticmethod
    def _level_to_str(level):
        if level == LogLevel.DEBUG:
            return 'DBG'
        elif level == LogLevel.INFO:
            return 'INFO'
        elif level == LogLevel.WARNING:
            return 'WARN'
        elif level == LogLevel.ERROR:
            return 'ERR'
        return ''

    @staticmethod
    def stringify(to_stringify):
        if list == type(to_stringify):
            return "\n".join([Logger.stringify(item) for item in to_stringify])
        if str != type(to_stringify):
            return to_stringify.__str__()
        return to_stringify

    def _maybe_log(self, message, level):
        if self._level_threshold > level:
            return
        if message is None or len(message) == 0:
            return

        tabs = "\t" * self._indentation
        lines = self.stringify(message).splitlines()
        lines = [lines[0]] + [tabs + "\t" + line for line in lines[1:]]
        print(
            "%s%s [%s] %s" % (
                tabs, self._level_to_str(level), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "\n".join(lines)
            )
        )

    def log(self, message, level=LogLevel.INFO, indent_after=0):
        self._maybe_log(message, level)

        if indent_after > 0:
            self.tab()
        elif indent_after < 0:
            self.untab()

    def tab(self):
        self._indentation += 1

    def untab(self):
        if self._indentation > 0:
            self._indentation -= 1

    def debug(self, message):
        self.log(message, LogLevel.DEBUG)

    def info(self, message, indent_after=0):
        self.log(message, LogLevel.INFO, indent_after)

    def warning(self, message, indent_after=0):
        self.log(message, LogLevel.WARNING, indent_after)

    def error(self, message, indent_after=0):
        self.log(message, LogLevel.ERROR, indent_after)
