from constants.log_level import LogLevel
from deprecated import deprecated

current_log_level = LogLevel.WARNING


def set_log_level(new_level):
    global current_log_level
    current_log_level = new_level


def stringify(to_stringify):
    if list == type(to_stringify):
        return "\n".join([stringify(item) for item in to_stringify])
    if str != type(to_stringify):
        return to_stringify.__str__()
    return to_stringify


@deprecated('Use a logger object instead.')
def log(message, level=LogLevel.INFO):
    global current_log_level
    if current_log_level > level:
        return
    print(stringify(message))


def l(message, level):
    log(message, level)
