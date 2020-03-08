from enum import Enum


class TaskType(Enum):
    """
    Type of a task: Does it represent a change at the beginning of an event or at its end?
    """
    START = 'start'
    END = 'end'
