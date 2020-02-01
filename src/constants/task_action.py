from enum import Enum


class TaskAction(Enum):
    START = 'start'
    FINISH = 'finish'
    WAIT = 'wait'
    REMOVE = 'remove'
