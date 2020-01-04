from enum import IntEnum


class Level(IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


current_log_level = Level.WARNING


def set_log_level(new_level):
    global current_log_level
    current_log_level = new_level


def stringify(to_stringify):
    if list == type(to_stringify):
        return "\n".join([stringify(item) for item in to_stringify])
    if str != type(to_stringify):
        return to_stringify.__str__()
    return to_stringify


def log(message, level=Level.INFO):
    global current_log_level
    if current_log_level > level:
        return
    print(stringify(message))


def l(message, level):
    log(message, level)
