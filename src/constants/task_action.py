from enum import Enum


class TaskAction(Enum):
    """
    Actions each task can request (it must always be one of those).
    """
    START = 'start'
    FINISH = 'finish'
    WAIT = 'wait'
    REMOVE = 'remove'
