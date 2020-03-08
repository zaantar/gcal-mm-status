from enum import IntEnum


class LogLevel(IntEnum):
    """
    Represents the severity of a log message.
    """
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
