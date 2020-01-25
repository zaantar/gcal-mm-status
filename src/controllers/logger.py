from constants.log_level import LogLevel


def stringify(to_stringify):
    if list == type(to_stringify):
        return "\n".join([stringify(item) for item in to_stringify])
    if str != type(to_stringify):
        return to_stringify.__str__()
    return to_stringify


class Logger:
    _level_threshold: LogLevel

    def __init__(self, level_threshold: LogLevel = LogLevel.INFO):
        self._level_threshold = level_threshold

    def set_level_threshold(self, new_threshold: LogLevel):
        self._level_threshold = new_threshold

    def log(self, message, level=LogLevel.INFO):
        if self._level_threshold > level:
            return
        print(stringify(message))
